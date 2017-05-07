# Django
from django.test import TestCase
from django.test.client import RequestFactory

# local Django
from exercise import (
    constants, views,
)
from exercise.models import (
    Exercise, UserExercise, TestCaseExercise,
)

from user.models import User

# 302 is the value returned from a HttpRequest status code when the URL was redirected.
REQUEST_REDIRECT = 302

class TestExerciseRegistration(TestCase):

    exercise = Exercise()

    def setUp(self):
        self.exercise.title = 'Basic Exercise'
        self.exercise.category = 2
        self.exercise.statement_question = '<p>Text Basic Exercise.</p>'
        self.exercise.score = 10
        self.exercise.deprecated = 0

    def test_str_is_correct(self):
        self.exercise.save()
        exercise_database = Exercise.objects.get(id=self.exercise.id)
        self.assertEqual(str(exercise_database), str(self.exercise))

    def test_if_exercise_is_saved_database(self):
        self.exercise.save()
        exercise_database = Exercise.objects.get(id=self.exercise.id)
        self.assertEqual(exercise_database, self.exercise)

    def test_exercise_get_title(self):
        self.exercise.save()
        exercise_database = Exercise.objects.get(id=self.exercise.id)
        self.assertEqual(exercise_database.title, self.exercise.title)

    def test_exercise_get_category(self):
        self.exercise.save()
        exercise_database = Exercise.objects.get(id=self.exercise.id)
        self.assertEqual(exercise_database.category, self.exercise.category)

    def test_exercise_get_statement_question(self):
        self.exercise.save()
        exercise_database = Exercise.objects.get(id=self.exercise.id)
        self.assertEqual(
                        exercise_database.statement_question,
                        self.exercise.statement_question)

    def test_exercise_get_score(self):
        self.exercise.save()
        exercise_database = Exercise.objects.get(id=self.exercise.id)
        self.assertEqual(exercise_database.score, self.exercise.score)

    def test_exercise_get_deprecated(self):
        self.exercise.save()
        exercise_database = Exercise.objects.get(id=self.exercise.id)
        self.assertEqual(
            exercise_database.deprecated,
            self.exercise.deprecated)


class TestUserExerciseRegistration(TestCase):

    exercise = Exercise()
    test_case_exercise = TestCaseExercise()
    user_exercise = UserExercise()
    user = User()

    def setUp(self):

        self.factory = RequestFactory()

        self.exercise.title = 'Basic Exercise'
        self.exercise.category = 2
        self.exercise.statement_question = '<p>Text Basic Exercise.</p>'
        self.exercise.score = 10
        self.exercise.deprecated = 0
        self.test_case_exercise.input_exercise = "a\n"
        self.test_case_exercise.output_exercise = ["B"]
        self.user.email = "user@user.com"
        self.user.password = "userpassword"
        self.user.first_name = "TestUser"
        self.user.username = "Username"
        self.user.is_active = True
        self.user_exercise.scored = False
        self.user_exercise.code = """
                                    #include <stdio.h>
                                    int main () {
                                        char c;
                                        scanf("%c", &c);
                                        printf("B");
                                        return 0;
                                    }
                                    """
        self.exercise.save()
        self.test_case_exercise.exercise = self.exercise
        self.test_case_exercise.save()
        self.user.save()
        self.user_exercise.user = self.user
        self.user_exercise.exercise = self.exercise

        self.user_exercise_valid_form = {
            'code': self.user_exercise.code
        }

        self.user_exercise_invalid_form = {
            'code': ''
        }

    def test_if_relation_user_exercise_saved_database(self):
        self.user_exercise.update_or_creates(
                                            self.user_exercise.code,
                                            self.user_exercise.exercise,
                                            self.user_exercise.user,
                                            self.user_exercise.time,
                                            self.user_exercise.status,
                                            self.user_exercise.scored)
        user_exercise_database = UserExercise.objects.get(
                                user=self.user,
                                exercise=self.exercise)
        self.assertEqual(str(user_exercise_database), str(self.user_exercise))

    def test_if_relation_user_exercise_is_updated(self):
        self.user_exercise.update_or_creates(
                                            self.user_exercise.code,
                                            self.user_exercise.exercise,
                                            self.user_exercise.user,
                                            self.user_exercise.time,
                                            self.user_exercise.status,
                                            self.user_exercise.scored)
        user_exercise_database = UserExercise.objects.get(
                                 user=self.user,
                                 exercise=self.exercise)
        self.assertEqual(str(user_exercise_database), str(self.user_exercise))

    def test_if_exercise_is_submitted(self):
        exercise_inputs = ['a\n', 'b\n']
        response = views.submit_exercise(
                                        self.user_exercise.code,
                                        exercise_inputs)
        self.assertIn("result", response)

    def test_if_extract_time_exercise_is_success(self):
        exercise_inputs = ['a\n', 'b\n']
        response = views.submit_exercise(
                                        self.user_exercise.code,
                                        exercise_inputs)
        runtime = views.extract_time(response)
        self.assertNotEqual(runtime, None)

    def test_if_extract_stdout_exercise_is_success(self):
        exercise_inputs = ['a\n', 'b\n']
        response = views.submit_exercise(
                                        self.user_exercise.code,
                                        exercise_inputs)
        stdout = views.extract_stdout(response)
        self.assertNotEqual(stdout, None)

    def test_get_all_input_exercise(self):
        list_all_input = views.get_all_input_exercise(self.exercise)
        length = len(list_all_input)
        self.assertNotEqual(length, 0)

    def test_get_all_ouput_exercise(self):
        list_all_output = views.get_all_output_exercise(self.exercise)
        length = len(list_all_output)
        self.assertNotEqual(length, 0)

    def test_if_user_exercise_is_incorrect(self):
        input_exercise = ['a\n', 'b\n']
        response = views.submit_exercise(
                                        self.user_exercise.code,
                                        input_exercise)
        stdout = views.extract_stdout(response)
        status = views.exercise_status(stdout, self.test_case_exercise.output_exercise)
        self.assertFalse(status)

    def test_if_user_exercise_is_correct(self):
        input_exercise = ['B']
        response = views.submit_exercise(
                                        self.user_exercise.code,
                                        input_exercise)
        stdout = views.extract_stdout(response)
        status = views.exercise_status(stdout, self.test_case_exercise.output_exercise)
        self.assertTrue(status)

    def test_if_user_scored_exercise(self):
        scored = False
        status = True
        response = views.scores_exercise(scored, self.user, self.exercise.score, status)
        self.assertTrue(response)

    def test_if_user_not_scored_exercise(self):
        scored = False
        status = False
        response = views.scores_exercise(scored, self.user, self.exercise.score, status)
        self.assertFalse(response)

    def test_if_user_already_scored_exercise(self):
        scored = True
        status = True
        response = views.scores_exercise(scored, self.user, self.exercise.score, status)
        self.assertTrue(response)

    def test_if_user_exercise_is_processed_valid_form(self):
        request = self.factory.post('/exercise/process/1/', self.user_exercise_valid_form)
        request.user = self.user
        response = views.process_user_exercise(request, self.exercise.id)
        self.assertEqual(response.status_code, REQUEST_REDIRECT)
        self.assertEqual(response.url, '/en/exercise/1/')

    def test_if_user_exercise_is_processed_invalid_form(self):
        request = self.factory.post('/exercise/process/1/', self.user_exercise_invalid_form)
        request.user = self.user
        response = views.process_user_exercise(request, self.exercise.id)
        self.assertEqual(response.status_code, REQUEST_REDIRECT)
        self.assertEqual(response.url, '/en/exercise/1/')


class TestCaseExerciseRegistration(TestCase):
    exercise = Exercise()
    test_case_exercise = TestCaseExercise()

    def setUp(self):
        self.exercise.title = 'Basic Exercise'
        self.exercise.category = 2
        self.exercise.statement_question = '<p>Text Basic Exercise.</p>'
        self.exercise.score = 10
        self.exercise.deprecated = 0
        self.test_case_exercise.input_exercise = "1 2\n"
        self.test_case_exercise.output_exercise = "2 1\n"

    def test_if_user_exercise_is_saved_database(self):
        self.exercise.save()
        self.test_case_exercise.exercise = self.exercise
        self.test_case_exercise.save()
        test_case_exercise_database = TestCaseExercise.objects.get(
                                    id=self.test_case_exercise.id)
        self.assertEqual(
                        str(test_case_exercise_database),
                        str(self.test_case_exercise))


class TestRequestExercise(TestCase):
    exercise = Exercise()
    test_case_exercise = TestCaseExercise()
    user = User()

    def setUp(self):
        self.user.email = "user@user.com"
        self.user.first_name = "TestUser"
        self.user.username = "Username"
        self.user.is_active = True
        self.exercise.title = 'Basic Exercise'
        self.exercise.category = 2
        self.exercise.statement_question = '<p>Text Basic Exercise.</p>'
        self.exercise.score = 10
        self.exercise.deprecated = 0
        self.test_case_exercise.input_exercise = "a\n"
        self.test_case_exercise.output_exercise = "B\n"
        self.factory = RequestFactory()
        self.user.set_password('userpassword')
        self.user.save()
        self.exercise.save()

        self.test_case_exercise.exercise = self.exercise
        self.test_case_exercise.save()

    def test_list_all_exercises_deprecated(self):
        request = self.factory.get('/exercise/')
        request.user = self.user
        response = views.list_all_exercises(request)
        self.assertEqual(response.status_code, constants.REQUEST_SUCCEEDED)

    def test_list_exercises_not_deprecated(self):
        request = self.factory.get('/exercise/')
        request.user = self.user
        response = views.list_exercises_not_deprecated(request)
        self.assertEqual(response.status_code, constants.REQUEST_SUCCEEDED)

    def test_show_exercise_is_valid(self):
        request = self.factory.get('/exercise/')
        request.user = self.user
        response = views.show_exercise(request, self.exercise.id)
        self.assertEqual(response.status_code, constants.REQUEST_SUCCEEDED)
