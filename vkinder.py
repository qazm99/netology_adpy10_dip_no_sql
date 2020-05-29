import vk
import psycopg2 as pg
import requests
from getpass import getpass
import math
import json
import random

from datetime import datetime as dt

from db_engine import (
    insert_update_likely_users,
    create_db_struct_vkinder,
    drop_table,
    get_likely_users, spec_list)
from qazm import posintput, StatusBar, list_from_string
from settings import COUNT_IN_SEARCH, USER_FIX, DATA_BASE, VK_V, APPLICATION_ID
from vkapi import (
    get_best_photo,
    find_group_all_users_list_25,
    api_reuest,
)


class VKUser:

    def __init__(
            self,
            user_vk_id,
            **kwargs
    ):
        self.user_vk_id = user_vk_id
        self.first_name = kwargs.get("first_name") if kwargs.get("first_name") else ""
        self.last_name = kwargs.get("last_name") if kwargs.get("last_name") else ""
        self.sex = kwargs.get("sex") if kwargs.get("sex") else 0
        self.city = kwargs.get("city") if kwargs.get("city") else 0
        self.age = kwargs.get("age") if kwargs.get("age") else 0
        self.activities = kwargs.get("activities") if kwargs.get("activities") else []
        self.interests = kwargs.get("interests") if kwargs.get("interests") else []
        self.movies = kwargs.get("movies") if kwargs.get("movies") else []
        self.music = kwargs.get("music") if kwargs.get("music") else []
        self.books = kwargs.get("books") if kwargs.get("books") else []
        self.quotes = kwargs.get("quotes") if kwargs.get("quotes") else []
        self.about = kwargs.get("about") if kwargs.get("about") else []
        self.home_town = kwargs.get("home_town") if kwargs.get("home_town") else []

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def url(self):
        return f"https://vk.com/id{self.user_vk_id}"


class TargetUser(VKUser):

    def __init__(
            self,
            user_vk_id,
            user_vk_login,
            user_vk_token,
            **kwargs

    ):
        super().__init__(
            user_vk_id,
            **kwargs
        )
        self.user_vk_login = user_vk_login
        self.user_vk_token = user_vk_token


class LikelyUser(VKUser):

    def __init__(
            self,
            user_vk_id,
            **kwargs
    ):
        super().__init__(
            user_vk_id,
            **kwargs
        )
        self.relation = kwargs.get("relation") if kwargs.get("relation") else 0
        self.common_friends = kwargs.get("common_friends") if kwargs.get("common_friends") else 0
        self.common_groups = kwargs.get("common_groups") if kwargs.get("common_groups") else 0
        self.points_auto = kwargs.get("points_auto") if kwargs.get("points_auto") else 0
        self.urls_photo = kwargs.get("urls_photo") if kwargs.get("urls_photo") else []

    def calculate_points_auto(self, current_target_user: TargetUser):

        common_activities = calc_common_param(current_target_user.activities, self.activities)
        common_interests = calc_common_param(current_target_user.interests, self.interests)
        common_movies = calc_common_param(current_target_user.movies, self.movies)
        common_music = calc_common_param(current_target_user.music, self.music)
        common_books = calc_common_param(
            current_target_user.books, self.books
        )
        common_quotes = calc_common_param(
            current_target_user.quotes, self.quotes
        )
        common_about = calc_common_param(
            current_target_user.about, self.about
        )
        common_home_town = calc_common_param(
            current_target_user.home_town, self.home_town
        )

        points_relation = calc_points(self.relation, {1: 5, 6: 15})
        points_age = calc_points(
            int(math.fabs(current_target_user.age - self.age)),
            {0: 20, 1: 17, 2: 15, 3: 12, 4: 10, 5: 5},
        )
        points_activities = calc_points(
            common_activities, {1: 10, 2: 20, 3: 30}
        )
        points_interests = calc_points(
            common_interests, {1: 10, 2: 20, 3: 30}
        )
        points_movies = calc_points(
            common_movies, {1: 10, 2: 13, 3: 15}
        )
        points_music = calc_points(common_music, {1: 20, 2: 25, 3: 30})
        points_books = calc_points(common_books, {1: 10, 2: 15, 3: 20})
        points_quotes = calc_points(
            common_quotes, {1: 10, 2: 20, 3: 30}
        )
        points_about = calc_points(common_about, {1: 10, 2: 20, 3: 30})
        points_home_town = calc_points(
            common_home_town, {1: 20, 2: 25, 3: 30}
        )
        points_common_friends = calc_points(
            self.common_friends, {1: 30, 2: 35, 3: 40}
        )

        self.points_auto = (
                points_age
                + points_relation
                + points_activities
                + points_interests
                + points_movies
                + points_music
                + points_books
                + points_quotes
                + points_about
                + points_home_town
                + points_common_friends
        )

    def user_to_db(self, connection, target_id_vk, status=None):

        if connection:
            params_user = dict(first_name=self.first_name,
                               last_name=self.last_name,
                               sex=self.sex,
                               city=self.city,
                               age=self.age,
                               activities=self.activities,
                               interests=self.interests,
                               movies=self.movies,
                               music=self.music,
                               books=self.books,
                               quotes=self.quotes,
                               about=self.about,
                               home_town=self.home_town,
                               urls_photo=self.urls_photo,
                               relation=self.relation,
                               common_friends=self.common_friends,
                               common_groups=self.common_groups,
                               points_auto=self.points_auto,
                               )

            if status is not None:
                params_user.update({'status': status})

            insert_update_likely_users(connection,
                                       target_id_vk,
                                       self.user_vk_id,
                                       **params_user)

    def user_from_db(self, connection, target_id_vk, user_vk_id):

        user_db = get_likely_users(connection, target_id_vk, user_vk_id)

        self.__init__(user_db[2], relation=user_db[17], common_friends=user_db[18],
                      common_groups=user_db[19], points_auto=user_db[20], urls_photo=user_db[16],
                      first_name=user_db[3], last_name=user_db[4], sex=user_db[5], city=user_db[6], age=user_db[7],
                      activities=user_db[8], interests=user_db[9], movies=user_db[10], music=user_db[11],
                      books=user_db[12], quotes=user_db[13], about=user_db[14], home_town=user_db[15])

    def __str__(self):
        return f"{super(LikelyUser, self).__str__()}: рейтинг-{self.points_auto}, {super(LikelyUser, self).url()}"


class SearchParametr:
    def __init__(
            self,
            q="",
            city=0,
            age_from=0,
            age_to=0,
            count=0,
            sex=0,
            has_photo=0,
            status=[0, ],
    ):
        self.q = q
        self.city = city
        self.age_from = age_from
        self.age_to = age_to
        self.count = count
        self.sex = sex
        self.has_photo = has_photo
        self.status = status

    def set_default(self):
        self.q = ""
        self.city = 0
        self.age_from = 0
        self.age_to = 0
        self.count = 0
        self.sex = 0
        self.has_photo = 0
        self.status = [0, ]


# list поиск количества пересечений в списках
def calc_common_param(in_list_first, in_list_second) -> int:
    if isinstance(in_list_first, (list, set)) and isinstance(
            in_list_second, (list, set)
    ):
        common_elements = set(in_list_first) & set(in_list_second)
        if len(common_elements) > 0:
            return len(common_elements)


# db vk_api пытаемся по логину получить доступ к API VK
def get_target_user_vkapi_of_login(
        current_login, vk_v, application_id
) -> (int, vk.API):
    vk_api = None
    target_user = None

    try:
        # пробуем получить токен
        password = getpass(prompt="Введите пароль:")
        session_vk_login = vk.AuthSession(
            application_id, current_login, password,
        )
        token = session_vk_login.access_token
        # логинимся через токен для его проверки
        session_vk = vk.Session(token)
        vk_api = vk.API(session_vk, timeout=60, v=vk_v)
        user_target_dict = vk_api.users.get(
            fields=[
                "city",
                "bdate",
                "sex",
                "status",
                "activities",
                "interests",
                "music",
                "movies",
                "personal",
                "relation",
                "common_count",
                "has_photo",
                "books",
                "quotes",
                "about",
                "home_town",
            ])[0]

        vk_id = user_target_dict.get("id")
        if vk_id:
            target_user: TargetUser = TargetUser(vk_id, user_vk_login=current_login, user_vk_token=token,
                                                 first_name=user_target_dict.get("first_name"),
                                                 last_name=user_target_dict.get("last_name"),
                                                 age=(int(dt.now().year) - int(user_target_dict.get("bdate")[-4:])),
                                                 sex=user_target_dict.get("sex"),
                                                 city=user_target_dict.get("city").get("id") if user_target_dict.get(
                                                     "city") else 0,
                                                 activities=list_from_string(user_target_dict.get("activities")),
                                                 interests=list_from_string(user_target_dict.get("interests")),
                                                 movies=list_from_string(user_target_dict.get("movies")),
                                                 music=list_from_string(user_target_dict.get("music")),
                                                 books=list_from_string(user_target_dict.get("books")),
                                                 quotes=list_from_string(user_target_dict.get("quotes")),
                                                 about=list_from_string(user_target_dict.get("about")),
                                                 home_town=list_from_string(user_target_dict.get("home_town")))

    except (vk.api.VkAPIError, vk.api.VkAuthError, requests.exceptions.ConnectionError, Exception) as e:
        if e.__str__().find("Errno 11001") > 0:
            print("Не могу подключиться к сайту, проверьте соединение")
        elif e.__str__().find("incorrect password") > 0:
            print(f"Пароль не верный")
        elif e.__str__().find("no access_token passed") > 0:
            print(f"Нет доступа, проверьте логин и пароль")
        else:
            print(f"Неизвестная ошибка {e}")

    if target_user and vk_api:
        return target_user, vk_api


def get_likely_id_for_target_id_from_db(connection, target_id_vk) -> set:
    users_in_bd = get_likely_users(connection, target_id_vk, 0)
    if users_in_bd:
        likely_users_id_in_bd = set(map(lambda user_db: user_db[2], users_in_bd))
        return likely_users_id_in_bd
    else:
        return set()


# db vk_api
def search_users_of_parametr(vk_api, search_p, current_target_user, likely_users_export):
    likely_users = list()
    count_all_iteration = len(search_p.status) * (
            search_p.age_to - search_p.age_from + 1
    )
    print("Поиск подходящих пользователей")
    status_bar_find = StatusBar(count_all_iteration)

    for current_status in search_p.status:
        count_errors = 0
        for current_age in range(search_p.age_from, search_p.age_to + 1):
            status_bar_find.plus(1)
            dict_search = dict(
                q=search_p.q,
                city=search_p.city,
                age_from=current_age,
                age_to=current_age,
                count=search_p.count,
                sex=search_p.sex,
                has_photo=search_p.has_photo,
                status=current_status,
                sort=random.choice((0, 1)),
                fields=[
                    "bdate",
                    "relation",
                    "city",
                    "common_count",
                    "sex",
                    "activities",
                    "interests",
                    "music",
                    "movies",
                    "books",
                    "quotes",
                    "about",
                    "home_town",
                ],
            )
            users_search = api_reuest(vk_api, "users.search", **dict_search)
            # счетчик ошибок, если на одном пользователе нет ответа, то выходим из цикла досрочно
            if not users_search:
                count_errors += 1
                if count_errors == 10:
                    break
                continue

            for user in users_search.get("items"):
                if user.get("id") not in likely_users_export:
                    try:
                        current_likely_user = LikelyUser(user.get("id"),
                                                         relation=current_status,
                                                         common_friends=user.get("common_count"),
                                                         common_groups=-1,
                                                         first_name=user.get("first_name"),
                                                         last_name=user.get("last_name"),
                                                         age=current_age,
                                                         city=search_p.city,
                                                         sex=user.get("sex"),
                                                         activities=list_from_string(user.get("activities")),
                                                         interests=list_from_string(user.get("interests")),
                                                         movies=list_from_string(user.get("movies")),
                                                         music=list_from_string(user.get("music")),
                                                         books=list_from_string(user.get("books")),
                                                         quotes=list_from_string(user.get("quotes")),
                                                         about=list_from_string(user.get("about")),
                                                         home_town=list_from_string(user.get("home_town")),
                                                         )
                        current_likely_user.calculate_points_auto(current_target_user)
                        likely_users.append(current_likely_user)

                    except TypeError as e:
                        print(f"Ошибка типов: {e}")
    if likely_users:
        return likely_users


# local вычисление рейтинга для каждого параметра
def calc_points(common_count, dict_points):
    if isinstance(common_count, int) and isinstance(dict_points, dict):
        points = dict_points.get(common_count)
        if not points:
            if common_count == 0:
                return 0
            else:
                return max(dict_points.values())
        else:
            return points
    else:
        return 0


# db vk_api поиск подходящих пользователей для текущего пользователя
def find_users_for_user(vk_api, current_target_user, likely_users_export):
    sex_dict = {1: 2, 2: 1}
    count_search_max = COUNT_IN_SEARCH
    q_string = ""
    search_p = SearchParametr(
        q_string,
        current_target_user.city,
        current_target_user.age - 5,
        current_target_user.age + 5,
        count_search_max,
        sex_dict.get(current_target_user.sex),
        1,
        [1, 6],
    )

    all_likely_users = search_users_of_parametr(
        vk_api, search_p, current_target_user, likely_users_export
    )

    return all_likely_users


# db vk_api
def calc_top_for_user(vk_api, current_target_user, find_users):
    if vk_api and True:
        # определяем топ 99 пользователей
        top_99 = sorted(find_users, key=lambda find_user_top: find_user_top.points_auto, reverse=True)[:99]

        # первый пользователь - целевой
        top_100_ids_vk = [current_target_user.user_vk_id]

        for find_user in top_99:
            top_100_ids_vk.append(find_user.user_vk_id)

        # забираем для них и текущего пользователя группы
        groups_top_100 = find_group_all_users_list_25(top_100_ids_vk, vk_api)
        groups_target_user = groups_top_100[0].get(current_target_user.user_vk_id)
        find_groups_dict = dict()

        for user_groups in groups_top_100[1:]:
            find_groups_dict.update(user_groups)

        for user in top_99:
            common_groups = calc_common_param(groups_target_user, find_groups_dict.pop(user.user_vk_id))

            if common_groups:
                pass
                user.common_groups = common_groups
                points_group = calc_points(common_groups, {1: 20, 2: 25, 3: 30})
                user.points_auto += points_group

        top_99.sort(key=lambda find_user_top: find_user_top.points_auto, reverse=True)
        return top_99


# db vk_api выгрузка в файл
def top_10_to_file_for_user(vk_api: vk.API, current_target_user: TargetUser, likely_users: list):
    dict_top10 = dict()
    current_top10 = likely_users[:10]
    status_bar_top10 = StatusBar(len(current_top10))
    print("Ищем самые лучшие фотографии пользователей")

    for user in current_top10:
        status_bar_top10.plus()
        url_user = user.url()
        list_best_photo = get_best_photo(vk_api, user.user_vk_id)
        user.urls_photo = list_best_photo
        dict_top10.update({user.user_vk_id: {"url": url_user, "photos": list_best_photo}})
    filename = f'{current_target_user.user_vk_id}_{dt.now().strftime("%y%m%d_%H%M%S")}.json'

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(dict_top10, file)

    return current_top10, filename


# добавляем данные пользователя которых нет на ВК
def update_param_target_users(target_user: TargetUser, vk_api):
    if target_user.sex not in (1, 2):  # пол
        sex_exist = None
        while not sex_exist:
            sex = input(
                "Выберете ваш пол: мужской введите - м, женский введите - ж: "
            ).lower()
            sex_dict = {"m": 2, "м": 2, "ж": 1}
            if sex_dict.get(sex):
                target_user.sex = sex_dict.get(sex)
                sex_exist = True

    if not target_user.city:  # город
        while not target_user.city:
            params_city = dict(
                q=input("Введите наименование вашего города: "), country_id=1
            )
            city_list = api_reuest(vk_api, "database.getCities", **params_city)
            if city_list:
                if city_list.get("count") > 0:
                    city_list_find = city_list.get("items")
                    print("0-Ввести другой город")
                    for number, city in enumerate(city_list_find, 1):
                        city_string = f'{number}-{city.get("title")}'
                        if city.get("area"):
                            city_string += f', {city.get("area")}'
                        if city.get("region"):
                            city_string += f', {city.get("region")}'
                        print(city_string)
                    city_number = (
                            posintput(
                                "Введите номер вашего города: ",
                                0,
                                len(city_list.get("items"), ),
                            )
                            - 1
                    )
                    if city_number >= 0:
                        target_user.city = city_list_find[city_number].get("id")
                else:
                    print("Не найдено подходящих городов, попробуйте снова")
            else:
                print("Поиск города не удался - попробуйте снова")

    if (not target_user.age) or (target_user.age > 150):  # возраст
        target_user.age = posintput("Введите свой возраст: ", 10, 150)

    if not target_user.activities:
        while not target_user.activities:
            target_user.activities = list_from_string(
                input("Введите через запятую вашу деятельность: ")
            )

    if not target_user.interests:
        while not target_user.interests:
            target_user.interests = list_from_string(
                input("Введите через запятую ваши интересы: ")
            )

    if not target_user.movies:
        while not target_user.movies:
            target_user.movies = list_from_string(
                input("Введите через запятую ваши любимые фильмы: ")
            )

    if not target_user.music:
        while not target_user.music:
            target_user.music = list_from_string(
                input("Введите через запятую вашу любимую музыку: ")
            )

    if not target_user.books:
        while not target_user.books:
            target_user.books = list_from_string(
                input("Введите через запятую ваши любимые книги: ")
            )

    if not target_user.quotes:
        while not target_user.quotes:
            target_user.quotes = list_from_string(
                input("Введите через запятую ваши любимые цитаты: ")
            )

    if not target_user.about:
        while not target_user.about:
            target_user.about = list_from_string(
                input("Расскажите немного о себе, кратко через запятую: ")
            )

    if not target_user.home_town:
        while not target_user.home_town:
            target_user.home_town = list_from_string(
                input("Введите свои любимые или родные города через запятую: ")
            )

    return True


def get_connection_db():
    try:
        connection_db = pg.connect(
            dbname=DATA_BASE.get("dbname"),
            user=DATA_BASE.get("user"),
            password=DATA_BASE.get("password"),
        )
        return connection_db
    except pg.DatabaseError:
        print(
            "Не удалось подключиться к базе данных, проверьте настроки в файле settings.py"
        )


# local
def main_run():
    """
        l – (login) – авторизация, необходима для начала поиска контактов;
        f – (find) – поиск подходящих контактов;
        d – (delete) – удаление данных, данная команда удалит все данные поиска;
        i – (import) – выгрузка в файл подходящих пользователей;
        b - (black list) - добавление в черный список пользователей из топ 100;
        w - (white list) - добавление в избранный список пользователей из топ 100;
        q - (quit) - команда, которая завершает выполнение программы;
        """
    print(
        "Вас приветствует программа VKinder!\n",
        "(Введите help, для просмотра списка поддерживаемых команд)\n",
    )

    connection_db = get_connection_db()
    if connection_db:
        create_db_struct_vkinder(connection_db)
    vk_api = None
    current_target_user = None
    top_99 = None
    while True:
        user_command = input("Введите команду - ").lower().strip()

        if user_command == "d":

            if connection_db:
                drop_table(connection_db, ["likely_users_vk"])
                create_db_struct_vkinder(connection_db)
            else:
                print('Нет подключения к базе данных')

        elif user_command == "l":
            vk_api = None
            current_target_user = None
            top_99 = None
            current_login = USER_FIX

            if not current_login:
                current_login = input("Введите логин ВК: ")
            target_user_vk_api = get_target_user_vkapi_of_login(
                current_login, VK_V, APPLICATION_ID
            )

            if target_user_vk_api:
                current_target_user: VKUser = target_user_vk_api[0]
                vk_api = target_user_vk_api[1]

            if vk_api:

                if update_param_target_users(current_target_user, vk_api):

                    print(
                        f"Добро пожаловать {current_target_user.first_name} "
                        f"{current_target_user.last_name}, "
                        f"ваша страница {current_target_user.url()}"
                    )
                else:
                    vk_api = None
                    print(
                        "Не удальось получить данные пользователя, попробуйте залогиниться еще раз"
                    )

            else:
                print("Не удалось авторизоваться на сайте VK")

        elif user_command in ("f", "i", "b", "w"):
            if vk_api:
                if user_command == "f":
                    # поиск подходящих пользователей
                    amount_count_in_search = 0
                    # список уже выгруженных пользователей
                    likely_users_export = get_likely_id_for_target_id_from_db(connection_db,
                                                                              current_target_user.user_vk_id)
                    if vk_api and current_target_user:
                        find_users = find_users_for_user(vk_api, current_target_user, likely_users_export)
                        if find_users:
                            amount_count_in_search = len(find_users)
                            # выборка пользователей для конкретного пользователя
                            top_99 = calc_top_for_user(vk_api, current_target_user, find_users)

                    print(
                        f"Поиск подходящих пользователей завершен, "
                        f"всего было найдено {amount_count_in_search} пользователей"
                    )
                    if top_99:
                        for num, user in enumerate(top_99, 1):
                            print(f"{num} {user}")

                elif user_command == "i":
                    if top_99:

                        if connection_db:
                            top_filtered = []
                            for user_top in top_99:
                                if user_top.user_vk_id not in likely_users_export:
                                    top_filtered.append(user_top)
                        else:
                            top_filtered = top_99

                        # Запись в файл подходящих пользователей
                        top_10, current_file_name = top_10_to_file_for_user(
                            vk_api, current_target_user, top_filtered
                        )

                        # Обновить список выгруженных пользователей
                        if current_file_name:
                            if connection_db:
                                with connection_db:
                                    for user in top_10:
                                        user.user_to_db(connection_db, current_target_user.user_vk_id)
                                likely_users_export = get_likely_id_for_target_id_from_db(connection_db,
                                                                                          current_target_user.user_vk_id)

                            print("Импорт топ 10 пользователей прошел успешно")
                            if input("Показать топ 10 пользователей?да(y)/нет(n): ").lower() in (
                                    "да",
                                    "yes",
                                    "y",
                            ):
                                for num, user in enumerate(top_10, 1):
                                    print(f"\n{num} {user.first_name} {user.last_name}: {user.url()}")
                                    if user.urls_photo:
                                        for num, photo_url in enumerate(user.urls_photo, 1):
                                            print(f"Фото{num} {photo_url}")
                    else:
                        print("Сначала нужно выполнить поиск пользователей (команда f)")

                elif user_command in ("b", "w"):
                    dict_type = {"b": -1, "w": 1}
                    # Добавление в черный/избранный список
                    if connection_db:
                        spec_list(connection_db, current_target_user.user_vk_id, top_99,
                                  type_list=dict_type.get(user_command))
                    else:
                        print("Нет соединения с базой данных")

            else:
                print("Вам необходимо авторизоваться (команда - l)")
        elif user_command == "q":
            if input("Действительно хотите выйти из программы?да(у)/нет(n)").lower() in (
                    "y",
                    "yes",
                    "да",
            ):
                break
        elif user_command in ("help", "h"):
            print(main_run.__doc__)
        else:
            print("Введите help для получения списка комманд")


if __name__ == "__main__":
    main_run()
