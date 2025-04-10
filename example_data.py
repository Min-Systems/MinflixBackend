import datetime
from user_models import *
from film_models import *

EXAMPLEFILMS = [
            Film(
                title="Echoes of Tomorrow",
                length=120,
<<<<<<< HEAD
                technical_location="Vancouver",
=======
                image_name="Vancouver",
>>>>>>> develop
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
<<<<<<< HEAD
                technical_location="Arizona",
=======
                image_name="Arizona",
>>>>>>> develop
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
<<<<<<< HEAD
                technical_location="Sydney",
=======
                image_name="Sydney",
>>>>>>> develop
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
<<<<<<< HEAD
                technical_location="Cape Canaveral",
=======
                image_name="Cape Canaveral",
>>>>>>> develop
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
<<<<<<< HEAD
                technical_location="London",
=======
                image_name="London",
>>>>>>> develop
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
        username="user1@example.com",
        password="securepassword1",
        date_registered=datetime.datetime.now(),
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
        username="user2@example.com",
        password="securepassword2",
        date_registered=datetime.datetime.now(),
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
