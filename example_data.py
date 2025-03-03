from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship
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

EXAMPLEUSERS = []