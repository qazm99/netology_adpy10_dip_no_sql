import unittest
import vk
import vkapi
import psycopg2 as pg
from unittest.mock import patch
from db_engine import create_table, drop_table, create_db_struct_vkinder, insert_update_likely_users, get_likely_users, \
     spec_list
from vkinder import VKUser, calc_common_param, calc_points, TargetUser, LikelyUser, update_param_target_users, \
    get_target_user_vkapi_of_login, SearchParametr, search_users_of_parametr
from fixtures.settings_test import DATA_BASE, USER_FIX, VK_V, APPLICATION_ID, USER_PASS
from fixtures.fix_data import (
    struct_table_test,
    test_target_user,
    test_vk_user, test_likely_user1,
)


class TestCommon(unittest.TestCase):
    def test_calc_common_param(self):
        list_first = ["one", "two", 3, 4]
        list_second = ["two", 4]
        list_wrong = [6, "seven", 8, "nine"]
        result_positive = calc_common_param(list_first, list_second)
        self.assertEqual(result_positive, 2)
        result_positive = calc_common_param(list_first, list_first)
        self.assertEqual(result_positive, len(list_first))
        result_negative = calc_common_param(list_first, list_wrong)
        self.assertIsNone(result_negative)

    def test_calc_points(self):
        dict_points = {10: 100, 20: 90, 30: 80, 40: 70}
        result = calc_points(30, dict_points)
        self.assertEqual(result, dict_points.get(30))
        result = calc_points(50, dict_points)
        self.assertEqual(result, max(dict_points.values()))
        result = calc_points(0, dict_points)
        self.assertEqual(result, 0)


class TestClass(unittest.TestCase):
    def test_vk_user(self):
        user_vk_id = test_vk_user.get("id_vk")
        user_for_test = VKUser(user_vk_id, **test_vk_user)
        self.assertEqual(user_for_test.user_vk_id, user_vk_id)
        self.assertEqual(user_for_test.first_name, test_vk_user.get("first_name"))
        self.assertEqual(user_for_test.last_name, test_vk_user.get("last_name"))
        self.assertEqual(user_for_test.sex, test_vk_user.get("sex"))
        self.assertEqual(user_for_test.city, test_vk_user.get("city"))
        self.assertEqual(user_for_test.age, test_vk_user.get("age"))
        self.assertEqual(user_for_test.activities, test_vk_user.get("activities"))
        self.assertEqual(user_for_test.interests, test_vk_user.get("interests"))
        self.assertEqual(user_for_test.movies, test_vk_user.get("movies"))
        self.assertEqual(user_for_test.music, test_vk_user.get("music"))
        self.assertEqual(user_for_test.quotes, test_vk_user.get("quotes"))
        self.assertEqual(user_for_test.about, test_vk_user.get("about"))
        self.assertEqual(user_for_test.home_town, test_vk_user.get("home_town"))

    def test_target_user(self):
        user_vk_id = test_target_user.get("id_vk")
        user_vk_login = test_target_user.get("login")
        user_vk_token = test_target_user.get("token")
        user_for_test = TargetUser(user_vk_id, user_vk_login, user_vk_token, **test_target_user)
        self.assertEqual(user_for_test.user_vk_id, user_vk_id)
        self.assertEqual(user_for_test.first_name, test_target_user.get("first_name"))
        self.assertEqual(user_for_test.last_name, test_target_user.get("last_name"))
        self.assertEqual(user_for_test.sex, test_target_user.get("sex"))
        self.assertEqual(user_for_test.city, test_target_user.get("city"))
        self.assertEqual(user_for_test.age, test_target_user.get("age"))
        self.assertEqual(user_for_test.activities, test_target_user.get("activities"))
        self.assertEqual(user_for_test.interests, test_target_user.get("interests"))
        self.assertEqual(user_for_test.movies, test_target_user.get("movies"))
        self.assertEqual(user_for_test.music, test_target_user.get("music"))
        self.assertEqual(user_for_test.quotes, test_target_user.get("quotes"))
        self.assertEqual(user_for_test.about, test_target_user.get("about"))
        self.assertEqual(user_for_test.home_town, test_target_user.get("home_town"))

    def test_likely_user(self):
        user_vk_id = test_likely_user1.get("id_vk")
        user_for_test = LikelyUser(user_vk_id,  **test_likely_user1)
        self.assertEqual(user_for_test.user_vk_id, user_vk_id)
        self.assertEqual(user_for_test.first_name, test_likely_user1.get("first_name"))
        self.assertEqual(user_for_test.last_name, test_likely_user1.get("last_name"))
        self.assertEqual(user_for_test.sex, test_likely_user1.get("sex"))
        self.assertEqual(user_for_test.city, test_likely_user1.get("city"))
        self.assertEqual(user_for_test.age, test_likely_user1.get("age"))
        self.assertEqual(user_for_test.activities, test_likely_user1.get("activities"))
        self.assertEqual(user_for_test.interests, test_likely_user1.get("interests"))
        self.assertEqual(user_for_test.movies, test_likely_user1.get("movies"))
        self.assertEqual(user_for_test.music, test_likely_user1.get("music"))
        self.assertEqual(user_for_test.quotes, test_likely_user1.get("quotes"))
        self.assertEqual(user_for_test.about, test_likely_user1.get("about"))
        self.assertEqual(user_for_test.home_town, test_likely_user1.get("home_town"))
        self.assertEqual(user_for_test.relation, test_likely_user1.get("relation"))
        self.assertEqual(user_for_test.common_friends, test_likely_user1.get("common_friends"))
        self.assertEqual(user_for_test.common_groups, test_likely_user1.get("common_groups"))
        self.assertEqual(user_for_test.points_auto, test_likely_user1.get("points_auto"))
        self.assertEqual(user_for_test.urls_photo, test_likely_user1.get("urls_photo"))

    def test_calculate_points_auto(self):
        target_user = TargetUser(test_target_user.get('id_vk'), test_target_user.get('login'),
                                 test_target_user.get('token'), **test_target_user)
        likely_user = LikelyUser(test_likely_user1.get('id_vk'), **test_likely_user1)
        likely_user.calculate_points_auto(target_user)
        self.assertGreater(likely_user.points_auto, 100)


class TestDB(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.connection_db = pg.connect(
            dbname=DATA_BASE.get("dbname"),
            user=DATA_BASE.get("user"),
            password=DATA_BASE.get("password"),
        )

    def setUp(self) -> None:
        drop_table(
            self.connection_db, ["likely_users_vk", ]
        )
        create_db_struct_vkinder(self.connection_db)

    def test_create_drop_table(self):
        drop_table(self.connection_db, ("test_table_vk",))
        with self.connection_db:
            with self.connection_db.cursor() as cursor:
                cursor.execute(
                    "select exists (select from pg_tables where tablename = 'test_table_vk')"
                )
                result_drop = cursor.fetchall()[0][0]
        self.assertFalse(result_drop)
        create_table(
            self.connection_db,
            struct_table_test.get("table_name"),
            *struct_table_test.get("parameters"),
        )
        with self.connection_db:
            with self.connection_db.cursor() as cursor:
                cursor.execute(
                    "select exists (select from pg_tables where tablename = 'test_table_vk')"
                )
                result_create = cursor.fetchall()[0][0]
        self.assertTrue(result_create)
        drop_table(self.connection_db, ("test_table_vk",))
        with self.connection_db:
            with self.connection_db.cursor() as cursor:
                cursor.execute(
                    "select exists (select from pg_tables where tablename = 'test_table_vk')"
                )
                result_drop = cursor.fetchall()[0][0]
        self.assertFalse(result_drop)

    def test_user_to_db_from_db(self):
        target_id_vk = test_target_user.get("id_vk")
        likely_id_vk = test_likely_user1.get('id_vk')
        likely_user_in = LikelyUser(likely_id_vk,**test_likely_user1)
        likely_user_in.user_to_db(self.connection_db, target_id_vk)
        likely_user_out = LikelyUser(0)
        likely_user_out.user_from_db(self.connection_db, target_id_vk, likely_id_vk)
        self.assertEqual(likely_user_in.user_vk_id, likely_user_out.user_vk_id)
        self.assertEqual(likely_user_in.first_name, likely_user_out.first_name)
        self.assertEqual(likely_user_in.last_name, likely_user_out.last_name)
        self.assertEqual(likely_user_in.sex, likely_user_out.sex)
        self.assertEqual(likely_user_in.city, likely_user_out.city)
        self.assertEqual(likely_user_in.age, likely_user_out.age)
        self.assertEqual(likely_user_in.activities, likely_user_out.activities)
        self.assertEqual(likely_user_in.interests, likely_user_out.interests)
        self.assertEqual(likely_user_in.movies, likely_user_out.movies)
        self.assertEqual(likely_user_in.music, likely_user_out.music)
        self.assertEqual(likely_user_in.books, likely_user_out.books)
        self.assertEqual(likely_user_in.quotes, likely_user_out.quotes)
        self.assertEqual(likely_user_in.about, likely_user_out.about)
        self.assertEqual(likely_user_in.urls_photo, likely_user_out.urls_photo)
        self.assertEqual(likely_user_in.relation, likely_user_out.relation)
        self.assertEqual(likely_user_in.common_friends, likely_user_out.common_friends)
        self.assertEqual(likely_user_in.common_groups, likely_user_out.common_groups)
        self.assertEqual(likely_user_in.points_auto, likely_user_out.points_auto)

    def test_insert_update_likely_users_get_likely_users(self):
        target_id_vk = test_target_user.get("id_vk")
        likely_id_vk = test_likely_user1.get('id_vk')
        likely_user_params = dict(test_likely_user1)
        likely_user_params.pop("id")
        likely_user_params.pop("id_vk")
        users_in_db = [insert_update_likely_users(self.connection_db, target_id_vk, likely_id_vk, **likely_user_params),
                       get_likely_users(self.connection_db, test_target_user.get("id_vk"),
                                        test_likely_user1.get("id_vk"))]
        for user_in_db in users_in_db:
            self.assertEqual(user_in_db[1], target_id_vk)
            self.assertEqual(user_in_db[2], likely_id_vk)
            self.assertEqual(user_in_db[3], likely_user_params.get('first_name'))
            self.assertEqual(user_in_db[4], likely_user_params.get('last_name'))
            self.assertEqual(user_in_db[5], likely_user_params.get('sex'))
            self.assertEqual(user_in_db[6], likely_user_params.get('city'))
            self.assertEqual(user_in_db[7], likely_user_params.get('age'))
            self.assertEqual(user_in_db[8], likely_user_params.get('activities'))
            self.assertEqual(user_in_db[9], likely_user_params.get('interests'))
            self.assertEqual(user_in_db[10], likely_user_params.get('movies'))
            self.assertEqual(user_in_db[11], likely_user_params.get('music'))
            self.assertEqual(user_in_db[12], likely_user_params.get('books'))
            self.assertEqual(user_in_db[13], likely_user_params.get('quotes'))
            self.assertEqual(user_in_db[14], likely_user_params.get('about'))
            self.assertEqual(user_in_db[15], likely_user_params.get('home_town'))
            self.assertEqual(user_in_db[16], likely_user_params.get('urls_photo'))
            self.assertEqual(user_in_db[17], likely_user_params.get('relation'))
            self.assertEqual(user_in_db[18], likely_user_params.get('common_friends'))
            self.assertEqual(user_in_db[19], likely_user_params.get('common_groups'))
            self.assertEqual(user_in_db[20], likely_user_params.get('points_auto'))


    def test_spec_list(self):
        type_list = -1
        target_id_vk = test_target_user.get("id_vk")
        likely_id_vk = test_likely_user1.get("id_vk")
        for user_id in range(0, 10):
            test_likely_user1.update({"first_name": f"first name {user_id+1}", "last_name": f"last name {user_id+1}"})
            likely_user_in = LikelyUser(likely_id_vk+user_id, **test_likely_user1)
            likely_user_in.user_to_db(self.connection_db, target_id_vk, type_list)
        with patch("db_engine.input", return_value='n'):
            users_in_black = spec_list(self.connection_db, target_id_vk, [], type_list)
        self.assertEqual(len(users_in_black), 10)


class TestApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # api
        cls.login = USER_FIX
        cls.password = USER_PASS
        cls.vk_v = VK_V
        cls.application_id = APPLICATION_ID
        session_vk_login = vk.AuthSession(cls.application_id, cls.login, cls.password,)
        session_vk = vk.Session(session_vk_login.access_token)
        cls.vk_api = vk.API(session_vk, timeout=60, v=cls.vk_v)

    def test_vk_execute_for_method(self):
        q1 = "Москва"
        q2 = "Скворцово"
        list_param = [dict(q=q1, country_id=1), dict(q=q2, country_id=1)]
        result = vkapi.vk_execute_for_method(
            self.vk_api, "database.getCities", list_param
        )
        self.assertIsInstance(result, list)
        self.assertEqual(result[0].get("count"), len(result[0].get("items")))
        for city in result[0].get("items"):
            self.assertGreaterEqual(city.get("title").lower().find(q1.lower()), 0)
        self.assertEqual(result[1].get("count"), len(result[1].get("items")))
        for city in result[1].get("items"):
            self.assertGreaterEqual(city.get("title").lower().find(q2.lower()), 0)

    def test_find_group_all_users_list_25(self):
        users_list = list(range(1, 101))
        groups_list = vkapi.find_group_all_users_list_25(users_list,self.vk_api)
        self.assertEqual(len(groups_list), len(users_list))
        for groups_dict in groups_list:
            self.assertEqual(len(groups_dict), 1)
            current_user_id = list(groups_dict.keys())[0]
            current_groups_list = groups_dict.get(current_user_id)
            if current_groups_list:
                for group in current_groups_list:
                    self.assertIsInstance(group, int)
            users_list.remove(current_user_id)
        self.assertEqual(len(users_list), 0)

    def test_api_reuest(self):
        q1 = "Москва"
        params = dict(q=q1, country_id=1)
        result = vkapi.api_reuest(self.vk_api, "database.getCities", **params)
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("count"), len(result.get("items")))
        for city in result.get("items"):
            self.assertGreaterEqual(city.get("title").lower().find(q1.lower()), 0)

    def test_get_best_photo(self):
        user_vk_id = 1
        result = vkapi.get_best_photo(self.vk_api, user_vk_id)
        self.assertIsInstance(result, list)
        for image in result:
            self.assertRegex(image, r"^https://[^\s]+jpg")

    def test_update_param_target_users(self):
        target_user = TargetUser(test_target_user.get('id_vk'), test_target_user.get('login'),
                                 test_target_user.get('token'))
        with patch("vkinder.input", side_effect=["м", "Москва", "activities1, activities2",
                                                 "interests1, interests2", "movies1, movies2",
                                                 "music1, music2", "books1, books2", "quotes1, quotes2",
                                                 "about1, about2", "home1, home2"]):
            with patch("vkinder.posintput", side_effect=[1, 55]):
                update_param_target_users(target_user, self.vk_api)
        self.assertEqual(target_user.sex, 2)
        self.assertEqual(target_user.city, 1)
        self.assertEqual(target_user.age, 55)
        self.assertEqual(target_user.activities, ["activities1", "activities2"])
        self.assertEqual(target_user.interests, ["interests1", "interests2"])
        self.assertEqual(target_user.movies, ["movies1", "movies2"])
        self.assertEqual(target_user.music, ["music1", "music2"])
        self.assertEqual(target_user.books, ["books1", "books2"])
        self.assertEqual(target_user.quotes, ["quotes1", "quotes2"])
        self.assertEqual(target_user.about, ["about1", "about2"])
        self.assertEqual(target_user.home_town, ["home1", "home2"])

    def test_get_target_user_vkapi_of_login(self):
        with patch("vkinder.getpass", return_value=self.password):
            result = get_target_user_vkapi_of_login(self.login, self.vk_v, self.application_id)
        self.assertIsInstance(result[0], TargetUser)
        self.assertIsInstance(result[1], vk.API)

    def test_search_users_of_parametr(self):
        current_target_user = TargetUser(test_target_user.get('id_vk'), 'login', 'token', **test_target_user)
        q_string = ''
        city = 1
        start_age = 25
        stop_age = 26
        count_search_max = 100
        sex = 1
        has_photo = 1
        status = [6, ]
        search_p = SearchParametr(
            q_string,
            city,
            start_age,
            stop_age,
            count_search_max,
            sex,
            has_photo,
            status
        )
        find_users = search_users_of_parametr(self.vk_api, search_p, current_target_user)
        for user in find_users:
            self.assertIsInstance(user, LikelyUser)


if __name__ == "__main__":
    unittest.main()
