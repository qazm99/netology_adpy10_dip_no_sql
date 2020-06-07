# test_calc_common_param
list_first_for_calc = ["one", "two", 3, {4: 5}]
list_second_for_calc = ["two", {4: 5}]
list_wrong_for_calc = [6, "seven", {8: "nine"}]

struct_table_test = dict(
    table_name="test_table_vk",
    parameters=(
        "id serial PRIMARY KEY",
        "id_vk integer UNIQUE NOT NULL",
        "login varchar(100)",
        "token varchar(100)",
        "first_name varchar(100)",
        "last_name varchar(100)",
        "sex integer",
        "city integer",
        "age integer",
        "activities varchar[]",
        "interests varchar[]",
        "movies varchar[]",
        "music varchar[]",
        "books varchar[]",
        "quotes varchar[]",
        "about varchar[]",
        "home_town varchar[]",
    ),
)

test_vk_user = {
    "id": 1,
    "id_vk": 999999,

    "first_name": "vk_user first name",
    "last_name": "vk_user last name",
    "sex": 2,
    "city": 1,
    "age": 99,
    "activities": ["vk_user activities1", "vk_user activities2"],
    "interests": ["vk_user interests1", "vk_user interests2"],
    "movies": ["vk_user movies1", "vk_user movies2"],
    "music": ["vk_user music1", "vk_user music2"],
    "books": ["vk_user books1", "vk_user books2"],
    "quotes": ["vk_user quotes1", "vk_user quotes2"],
    "about": ["vk_user about1", "vk_user about2"],
    "home_town": ["vk_user home_town1", "vk_user home_town2"],
}

test_target_user = {
    "id": 4,
    "id_vk": 666666,
    "login": "target login",
    "token": "026f8e459c8f89ef75fa7a78265a0025",
    "first_name": "target first name",
    "last_name": "target last name",
    "sex": 2,
    "city": 1,
    "age": 99,
    "activities": ["target activities1", "common activities2"],
    "interests": ["target interests1", "common interests2"],
    "movies": ["target movies1", "common movies2"],
    "music": ["target music1", "common music2"],
    "books": ["target books1", "common books2"],
    "quotes": ["target quotes1", "common quotes2"],
    "about": ["target about1", "common about2"],
    "home_town": ["target home_town1", "common home_town2"],
}

test_likely_user1 = {
    "id": 2,
    "id_vk": 777777,
    "first_name": "likely_user1 first name",
    "last_name": "likely_user1 last name",
    "sex": 1,
    "city": 1,
    "age": 33,
    "activities": ["likely_user1 activities1", "common activities2"],
    "interests": ["likely_user1 interests1", "common interests2"],
    "movies": ["likely_user1 movies1", "common movies2"],
    "music": ["likely_user1 music1", "common music2"],
    "books": ["likely_user1 books1", "common books2"],
    "quotes": ["likely_user1 quotes1", "common quotes2"],
    "about": ["likely_user1 about1", "common about2"],
    "home_town": ["likely_user1 home_town1", "common home_town2"],
    "relation": 1,
    "common_friends": 5,
    "common_groups": 10,
    "points_auto": 55,
    "urls_photo": ["likely_user1 url photo 1", "likely_user1 url photo 2"],
}

test_user2 = {
    "id": 3,
    "id_vk": 888888,
    "first_name": "user first name",
    "last_name": "user last name",
    "sex": 1,
    "city": 1,
    "age": 55,
    "activities": ["activities1", "activities2"],
    "interests": ["interests1", "interests2"],
    "movies": ["movies1", "movies2"],
    "music": ["music1", "music2"],
    "books": ["books1", "books2"],
    "quotes": ["quotes1", "quotes2"],
    "about": ["about1", "about2"],
    "home_town": ["home_town1", "home_town2"],
    "relation": 6,
}

# test_grade1 = {
#     "id": 1,
#     "target_users_id": 1,
#     "users_id": 2,
#     "points_auto": 100,
#     "points_user": 90,
#     "num_common_friends": 10,
#     "num_common_groups": 20,
#     "export_state": True,
# }
#
# test_grade2 = {
#     "id": 2,
#     "target_users_id": 1,
#     "users_id": 3,
#     "points_auto": 50,
#     "points_user": 70,
#     "num_common_friends": 5,
#     "num_common_groups": 30,
#     "export_state": False,
# }
