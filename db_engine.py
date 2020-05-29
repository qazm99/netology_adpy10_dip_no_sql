import psycopg2 as pg


def create_table(connection: pg.connect, table_name, *columns):  # создает таблицы
    if isinstance(table_name, str):
        string_columns = ""
        for column in columns:
            if isinstance(column, str):
                string_columns += column + ", "
        string_columns = string_columns.strip(", ")
        with connection.cursor() as cursor:
            if string_columns > "":
                try:
                    cursor.execute(
                        f"CREATE TABLE IF NOT EXISTS {table_name} ({string_columns})"
                    )
                    return True
                except pg.DatabaseError as e:
                    print(f"Не удалось создать таблицу по причине: {e}")
    return False


def create_db_struct_vkinder(connection):
    table_list = [
        {
            "table_name": "likely_users_vk",
            "parameters": (
                "id serial PRIMARY KEY",  # 0
                "target_id_vk integer NOT NULL",
                "likely_id_vk integer NOT NULL",
                "first_name varchar(100)",
                "last_name varchar(100)",
                "sex integer",  # 5
                "city integer",
                "age integer",
                "activities varchar[]",
                "interests varchar[]",
                "movies varchar[]",  # 10
                "music varchar[]",
                "books varchar[]",
                "quotes varchar[]",
                "about varchar[]",
                "home_town varchar[]",  # 15
                "urls_photo varchar[]",
                "relation integer",
                "common_friends integer",
                "common_groups integer",
                "points_auto integer",  # 20
                "status integer DEFAULT 0",
                "UNIQUE (target_id_vk, likely_id_vk)",
            ),
        },

    ]
    for table in table_list:
        with connection:
            create_table(connection, table.get("table_name"), *table.get("parameters"))


def drop_table(connection, table_names):
    drop_all_table_flag = True
    for table_name in table_names:
        with connection:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(f"DROP TABLE {table_name} CASCADE")
                except pg.DatabaseError:
                    drop_all_table_flag = False
    if drop_all_table_flag:
        print("Все данные были удалены")
        return False
    else:
        print("Не все данные удалены")
        return True


def insert_update_likely_users(connection, target_users_id, users_id, **kwargs):
    with connection.cursor() as cursor:
        columns_list = []
        values_list = []
        for column, value in kwargs.items():
            columns_list.append(column)
            values_list.append(value)
        columns_string = ", ".join(columns_list)
        s_string = len(values_list) * ", %s"
        columns_string_update = ", ".join(
            map(lambda column_in_list: f"{column_in_list} = EXCLUDED.{column_in_list}", columns_list)
        )
        sql_string = (
            f"INSERT INTO likely_users_vk (target_id_vk, likely_id_vk, {columns_string}) "
            f"VALUES ({target_users_id}, {users_id} {s_string}) "
            f"ON CONFLICT (target_id_vk, likely_id_vk) DO UPDATE SET "
            f"{columns_string_update} "
            f"RETURNING *"
        )

        cursor.execute(sql_string, values_list)
        result = cursor.fetchall()[0]
        return result


def get_likely_users(connection, target_id, users_vk_id, status=None):
    if isinstance(status, int):
        sql_string_filter_status = f"and (status = {status})"
    else:
        sql_string_filter_status = ""

    if isinstance(users_vk_id, (tuple, list, set)):
        list_to_result: bool = True
        sql_string_filter_users = "and (likely_id_vk in (" + ", ".join(users_vk_id) + "))"
    elif users_vk_id == 0:
        list_to_result: bool = True
        sql_string_filter_users = ""
    else:
        list_to_result: bool = False
        sql_string_filter_users = f"and (likely_id_vk = {users_vk_id})"

    sql_string = (
        f"select * from  likely_users_vk "
        
        f"where (target_id_vk = {target_id}) {sql_string_filter_users}"
        f"{sql_string_filter_status} ORDER BY points_auto DESC"
    )
    if connection:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(sql_string)
                result = cursor.fetchall()
                if result:
                    if list_to_result:
                        return result
                    else:
                        return result[0]
    else:
        print("Нет связи с базой данных")


def get_likely_users_of_target_id_vk(
    connection: pg.connect,
    table_name: str,
    ids_vk: (list, tuple, set),
    bd: bool = False,
) -> list:
    id_str = "id" if bd else "target_id_vk"
    ids_vk_string = ", ".join(map(str, ids_vk))
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"select * from {table_name} where {id_str} in ({ids_vk_string})"
            )
            result_likely_users_vk = cursor.fetchall()
            if result_likely_users_vk:
                return result_likely_users_vk


def spec_list(connection_db, target_id_vk, top_list, type_list: int) -> list:
    if type_list == -1:
        str_list = "черный список"
    elif type_list == 1:
        str_list = "избранный список"
    else:
        str_list = "спец список"

    if input(f"Добавить в {str_list} пользователя? да(у)/нет(n)").lower() in (
        "да",
        "yes",
        "y"
    ):
        if top_list:
            for num, user in enumerate(top_list,1):
                print(f"{num} {user}")
            users_to_black_list = set(
                input(
                    f"Введите номера пользователей для добавления их в {str_list} через пробел "
                ).split(" ")
            )
            with connection_db:
                for user_to_black in users_to_black_list:
                    if user_to_black.isdigit():
                        user_id_int = int(user_to_black)
                        if user_id_int <= len(top_list):
                            # добавляем из топ листа в блэк лист
                            top_list[user_id_int - 1].user_to_db(connection_db,target_id_vk, status=type_list)
                            print(f"В {str_list} добавили {top_list[user_id_int - 1]}")
        else:
            print("Топ лист пуст")

    spec_list_users_db = get_likely_users(connection_db, target_id_vk, 0, status=type_list)
    if spec_list_users_db:
        print(str_list.capitalize())
        black_list_users = []
        for num, user_db in enumerate(spec_list_users_db, 1):
            from vkinder import LikelyUser
            temp_user = LikelyUser(0)
            temp_user.user_from_db(connection_db, user_db[1], user_db[2])
            current_likely_user = temp_user
            print(f"{num} {current_likely_user}")
            black_list_users.append(current_likely_user)
    else:
        print(f"Увы, {str_list} пуст")
