from models import *

EXAMPLEFILMS = [
            Film(
                title="Echoes of Tomorrow",
                length=120,
                technical_location="Vancouver",
                producer="Elena Garcia",
                film_cast=[
                    FilmCast(name="Liam Walker", role="Time Traveler"),
                    FilmCast(name="Sophia Bennett", role="Scientist"),
                    FilmCast(name="James Porter", role="Antagonist"),
                ],
                production_team=[
                    FilmProductionTeam(name="Martha Lin", role="Director"),
                    FilmProductionTeam(name="Carlos Reyes", role="Cinematographer"),
                    FilmProductionTeam(name="David Kim", role="Composer"),
                ],
            ),
            Film(
                title="Under the Crimson Sun",
                length=140,
                technical_location="Arizona",
                producer="Jackson King",
                film_cast=[
                    FilmCast(name="Amelia Hart", role="Heroine"),
                    FilmCast(name="Oscar Blake", role="Villager"),
                    FilmCast(name="Evelyn Brooks", role="Villain"),
                ],
                production_team=[
                    FilmProductionTeam(name="Ryan Turner", role="Director"),
                    FilmProductionTeam(name="Sophia Lee", role="Sound Designer"),
                    FilmProductionTeam(name="Hunter Mitchell", role="Stunt Coordinator"),
                ],
            ),
            Film(
                title="The Whispering Waves",
                length=130,
                technical_location="Sydney",
                producer="Diana Hughes",
                film_cast=[
                    FilmCast(name="Oliver Hale", role="Lighthouse Keeper"),
                    FilmCast(name="Chloe Morgan", role="Marine Biologist"),
                    FilmCast(name="Harper Gray", role="Tour Guide"),
                ],
                production_team=[
                    FilmProductionTeam(name="Grant Adams", role="Director"),
                    FilmProductionTeam(name="Nina Young", role="VFX Artist"),
                    FilmProductionTeam(name="Jacob Walker", role="Sound Engineer"),
                ],
            ),
            Film(
                title="Starlight Odyssey",
                length=150,
                technical_location="Cape Canaveral",
                producer="Henry Wells",
                film_cast=[
                    FilmCast(name="Evelyn James", role="Astronaut"),
                    FilmCast(name="Daniel Cole", role="Scientist"),
                    FilmCast(name="Isla Parker", role="Alien"),
                ],
                production_team=[
                    FilmProductionTeam(name="Sophia Reed", role="Director"),
                    FilmProductionTeam(name="Max Young", role="Editor"),
                    FilmProductionTeam(name="Zara Lee", role="Costume Designer"),
                ],
            ),
            Film(
                title="Chasing Shadows",
                length=110,
                technical_location="London",
                producer="Victoria Hayes",
                film_cast=[
                    FilmCast(name="Emma Brown", role="Detective"),
                    FilmCast(name="Noah Carter", role="Suspect"),
                    FilmCast(name="Lucas Green", role="Witness"),
                ],
                production_team=[
                    FilmProductionTeam(name="Ethan White", role="Director"),
                    FilmProductionTeam(name="Liam Gray", role="Composer"),
                    FilmProductionTeam(name="Ava Brooks", role="Cinematographer"),
                ],
            ),
        ]

EXAMPLEUSERS = [
    FilmUser(
        email="user1@example.com",
        password="securepassword1",
        date_registered="2025",
        profiles=[
            Profile(
                displayname="user1profile1",
                search_history=[
                    SearchHistory(
                        search_query="example_query_1_user1_pf1"
                    ),
                    SearchHistory(
                        search_query="example_query_2_user1_pf1"
                    )
                ],
                favorites=[
                    Favorite(
                        film_id=2,
                        favorited_date="2021"
                    ),
                    Favorite(
                        film_id=1,
                        favorited_date="2022"
                    )
                ],
                watch_later=[
                    WatchLater(
                        film_id=4,
                        dateadded="2021"
                    ),
                ],
                watch_history=[
                    WatchHistory(
                        film_id=3,
                        timestamp=5,
                        completion=2,
                        datewatched="2021"
                    )
                ]
            ),
            Profile(
                displayname="user1profile2",
                search_history=[
                    SearchHistory(
                        search_query="example_query_1_user1_pf2"
                    ),
                    SearchHistory(
                        search_query="example_query_2_user1_pf2"
                    )
                ],
                favorites=[
                    Favorite(
                        film_id=2,
                        favorited_date="2022"
                    ),
                    Favorite(
                        film_id=1,
                        favorited_date="2021"
                    )
                ],
                watch_later=[
                    WatchLater(
                        film_id=3,
                        dateadded="2022"
                    )
                ],
                watch_history=[
                    WatchHistory(
                        film_id=3,
                        timestamp=4,
                        completion=10,
                        datewatched="2025"
                    )
                ]
            )
        ]
    ),
    FilmUser(
        email="user2@example.com",
        password="securepassword2",
        date_registered="2024",
        profiles = [
            Profile(
                displayname="user2profile1",
                search_history=[
                    SearchHistory(
                        search_query="example_query_1_user2_pf1"
                    ),
                    SearchHistory(
                        search_query="example_query_2_user2_pf1"
                    )
                ],
                favorites=[
                    Favorite(
                        film_id=2,
                        favorited_date="2022"
                    ),
                    Favorite(
                        film_id=1,
                        favorited_date="2021"
                    )
                ],
                watch_later=[
                    WatchLater(
                        film_id=3,
                        dateadded="2022"
                    )
                ],
                watch_history=[
                    WatchHistory(
                        film_id=3,
                        timestamp=4,
                        completion=10,
                        datewatched="2025"
                    )
                ]
            )
        ]
    ) 
]

'''
# Sample data
example_users = [
    FilmUser(id=1, email="user1@example.com", password="securepassword1", date_registered="2023"),
    FilmUser(id=2, email="user2@example.com", password="securepassword2", date_registered="2024"),
]

example_profiles = [
    Profile(id=1, userid=1, displayname="FilmUser1_Profile1"),
    Profile(id=2, userid=2, displayname="FilmUser2_Profile1"),
]

example_search_history = [
    SearchHistory(id=1, profileid=1, film_id=1, search_query="Action Movies"),
    SearchHistory(id=2, profileid=2, film_id=3, search_query="Romantic Comedies"),
]

example_favorites = [
    Favorite(id=1, profileid=1, film_id=2, favorited_date="2022"),
    Favorite(id=2, profileid=2, film_id=4, favorited_date="2021"),
]

example_watch_later = [
    WatchLater(id=1, profileid=1, film_id=5, dateadded="2023"),
    WatchLater(id=2, profileid=2, film_id=1, dateadded="2022"),
]

example_watch_history = [
    WatchHistory(id=1, profileid=1, film_id=3, timestamp=3600, completion=100.0, datewatched="2020"),
    WatchHistory(id=2, profileid=2, film_id=2, timestamp=1800, completion=50.0, datewatched="2021"),
]
'''