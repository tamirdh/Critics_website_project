import mysql.connector as mysql
from new_york_api import nyApi
from tmdb import tmdbApi
import json


def parse_ny_tables():
    ny_api = nyApi()
    try:
        connection = connect_to_db()
        # insert_critics(ny_api, connection)
        insert_reviews(connection, ny_api)
    except Exception:
        print("Falied")
        raise
    finally:
        connection.close()


def insert_critics(ny_api: nyApi, connection: mysql):
    critics = ny_api.get_all_critics()
    cursor = connection.cursor()
    try:
        for critic in critics:

            name = critic["display_name"]
            try:
                bio = critic["bio"].replace('"', '\"').replace("'", "\'")
            except (KeyError, AttributeError):
                bio = None
            try:
                image = critic["multimedia"]["resource"]["src"]
            except (KeyError, TypeError):
                image = None

            query = 'INSERT INTO Person (name) VALUE ("{0}");'.format(name)
            cursor.execute(query)
            connection.commit()
            query = ' INSERT INTO Critic (bio, image, ID) VALUES (%s, %s, %s);'
            cursor.execute(query, params=(bio, image, cursor.lastrowid))
            connection.commit()
        print("Insert critics complete")
    except Exception:
        print("Insert into critic failed, check manually")
        raise
    finally:
        cursor.close()


def insert_single_critic(connection: mysql, name: str):
    cursor = connection.cursor()
    try:
        query = 'INSERT INTO Person (name) VALUE ("{0}");'.format(name)
        cursor.execute(query)
        connection.commit()
        query = ' INSERT INTO Critic (bio, image, ID) VALUES (%s, %s, %s);'
        cursor.execute(query, params=(None, None, cursor.lastrowid))
        connection.commit()
    except Exception:
        print("Single insert critic failed")
        raise
    finally:
        cursor.close()


def insert_reviews(connection: mysql, ny_api: nyApi):
    cursor = connection.cursor()
    try:
        for offset in range(440, 10000, 20):
            print("Offset: {}".format(offset))
            reviews = ny_api.get_all_reviews(offset=offset)
            query = "INSERT INTO Review(movie_id, critics_pick, critic_id, headline, summary, date, link) VALUES" \
                    "(%s, %s, %s, %s, %s, %s, %s)"
            for review in reviews:
                movie_title = review["display_title"]
                if not movie_title:
                    continue
                critic_name = " ".join(w.capitalize() for w in review["byline"].split())  # Make it CamelCase
                critic_id = get_person_id(connection, critic_name)
                if not critic_id:
                    print("Critic {} not found".format(critic_name))
                    insert_single_critic(connection, critic_name)
                    critic_id = get_person_id(connection, critic_name)
                    if not critic_id:
                        continue
                movie_id = get_movie_id(connection, movie_title)
                if not movie_id:
                    print("Movie {} not found".format(movie_title))
                    continue
                if get_review(connection, critic_id, movie_id):
                    print("Already inserted to DB")
                    continue
                params = (movie_id, review["critics_pick"], critic_id, review["headline"], review["summary_short"],
                          review["publication_date"], review["link"]["url"])
                cursor.execute(query, params=params)
                connection.commit()
    except Exception:
        print("Reviews insert failed")
        raise
    finally:
        cursor.close()


def get_review(connection, critic_id, movie_id):
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM Review where critic_id = %s and movie_id = %s"
        cursor.execute(query, (critic_id, movie_id))
        result = cursor.fetchone()
        return result
    except Exception:
        print("Get review failed")
        raise
    finally:
        cursor.close()


def parse_tmdb_tables():
    tmdb = tmdbApi()
    connection = connect_to_db()
    try:
        # insert_genres(tmdb, connection)
        # insert_popular_movies(tmdb, connection)
        insert_actors(connection, tmdb)
    except Exception:
        connection.close()
        raise
    finally:
        connection.close()


def insert_genres(tmdb: tmdbApi, connection: mysql):
    genres = tmdb.get_movie_genres()
    cursor = connection.cursor()
    try:
        for genre in genres:
            oid = genre["id"]
            name = genre["name"]
            query = "INSERT INTO Genre (ID, category_name) VALUES (%s, %s)"
            cursor.execute(query, params=(oid, name))
            connection.commit()
        print("Insert genres complete")
    except Exception:
        print("Inserting genres failed")
        raise
    finally:
        cursor.close()


def insert_director(tmdb: tmdbApi, connection: mysql, director_id: str):
    cursor = connection.cursor()
    try:
        person_data = tmdb.get_person(director_id)
        name = person_data["name"]
        gender = person_data["gender"]
        birthday = person_data["birthday"]
        bio = person_data["biography"]
        query = 'INSERT INTO Person (name) VALUE ("{0}");'.format(name)
        cursor.execute(query)
        connection.commit()
        query = 'INSERT INTO Director(ID, gender, birthday, bio) VALUES (%s, %s, %s, %s)'
        cursor.execute(query, params=(cursor.lastrowid, gender, birthday, bio))
        connection.commit()
        return cursor.lastrowid
    except Exception:
        print("Directors insert failed")
        raise
    finally:
        cursor.close()


def get_person_id(connection: mysql, name: str):
    query = "SELECT ID from Person WHERE name=%s".format(name)
    cursor = connection.cursor()
    try:
        cursor.execute(query, (name,))
        result = cursor.fetchone()
        if result:
            return result[0]

        return result
    except Exception:
        print("Can't find directors id, query: {0}".format(query))
        raise
    finally:
        cursor.close()


def get_movie_id(connection: mysql, name: str):
    query = 'SELECT ID from Movie WHERE title=%s'
    cursor = connection.cursor()
    try:
        cursor.execute(query, (name,))
        result = cursor.fetchone()
        if result:
            return result[0]

        return result
    except Exception:
        print("Can't find movie id")
        raise
    finally:
        cursor.close()


def insert_popular_movies(tmdb: tmdbApi, connection: mysql):
    cursor = connection.cursor()
    try:
        for page in range(1, 500):
            print("Page: {}".format(page))
            movies = tmdb.get_movie_popular(page=page)
            query = "INSERT INTO Movie(title, category_id, director_id, release_date, length, vote_avg, vote_count)" \
                    " VALUES(%s, %s, %s, %s, %s, %s, %s)"
            for movie in movies:
                movie_id = movie["id"]
                if get_movie_id(connection, movie["title"]):
                    print("Movie already exists in our DB")
                    continue
                movie_credits = tmdb.get_movie_credits(movie_id)
                if not movie_credits:
                    continue
                extra_data = tmdb.get_movie_by_id(movie_id)
                if not extra_data:
                    continue

                director = get_director(movie_credits["crew"])
                if not director:
                    continue
                dir_id = get_person_id(connection, director["name"])
                if not dir_id:
                    insert_director(tmdb, connection, director["id"])
                    dir_id = get_person_id(connection, director["name"])
                # params = (title, genre, dir_id,release_date, length,vote_avg, vote_count)
                try:
                    params = (
                        movie["title"], movie["genre_ids"][0], dir_id, movie["release_date"], extra_data["runtime"],
                        movie["vote_average"], movie["vote_count"])
                    cursor.execute(query, params=params)
                except (KeyError, IndexError, mysql.DataError):
                    continue

                connection.commit()
                print("Movie {} inserted".format(movie["title"]))

    except Exception:
        print("Movie insertion failed")
        raise
    finally:
        cursor.close()


def insert_actors(connection: mysql, tmdb: tmdbApi):
    cursor = connection.cursor()
    try:
        for page in range(1, 500):
            print("Page: {}".format(page))
            movies = tmdb.get_movie_popular(page=page)

            for movie in movies:
                movie_id = movie["id"]
                our_movie_id = get_movie_id(connection, movie["title"])
                if not our_movie_id:
                    print("Movie {} doesn't exists in our DB".format(movie["title"]))
                    continue
                movie_credits = tmdb.get_movie_credits(movie_id)
                if not movie_credits:
                    continue
                for actor in movie_credits["cast"]:
                    name = actor["name"]
                    gender = actor["gender"]
                    actor_data = tmdb.get_person(actor["id"])
                    birthday = actor_data["birthday"]
                    bio = actor_data["biography"]
                    popularity = actor_data["popularity"]
                    actor_id = get_person_id(connection, name)
                    if not actor_id:
                        query = "INSERT INTO Person (name) VALUE (%s)"
                        cursor.execute(query, params=(name,))
                        connection.commit()
                        actor_id = get_person_id(connection, name)
                        if not actor_id:
                            print("Actor insert failed")
                            continue
                    if not check_actor(connection, actor_id):
                        query = "INSERT INTO Actor(ID, gender, birthday, bio, popularity) VALUES (%s, %s, %s, %s, %s)"
                        cursor.execute(query, params=(actor_id, gender, birthday, bio, popularity))
                        connection.commit()
                    if not check_appearance(connection, actor_id, our_movie_id):
                        query = "INSERT INTO Appearances(movie_id, actor_id) VALUES(%s, %s)"
                        cursor.execute(query, params=(our_movie_id, actor_id))
                        connection.commit()
    except Exception:
        print("Actor inserts failed")
        raise
    finally:
        cursor.close()


def check_appearance(connection, actor_id, movie_id):
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM Appearances WHERE actor_id=%s and movie_id=%s"
        cursor.execute(query, (actor_id, movie_id))
        result = cursor.fetchone()
        if result:
            return True
        else:
            return False
    except Exception:
        print("Appearance validation failed")
        raise
    finally:
        cursor.close()


def check_actor(connection, actor_id):
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM Actor WHERE Id=%s"
        cursor.execute(query, (actor_id,))
        result = cursor.fetchone()
        if result:
            return True
        else:
            return False
    except Exception:
        print("Appearance validation failed")
        raise
    finally:
        cursor.close()


def get_director(crew_data: dict):
    for person in crew_data:
        if person["job"] == "Director":
            return person
    return None


def connect_to_db():
    with open("api_creds.json") as cred_source:
        data = json.load(cred_source)
    connection = mysql.connect(host=data["our_db"]["host"], port=data["our_db"]["port"],
                               user=data["our_db"]["username"], password=data["our_db"]["password"],
                               database=data["our_db"]["db name"])
    if not connection.is_connected():
        print("Couldn't connect to DB, check credentials file")
        raise ConnectionError(connection)
    return connection


if __name__ == '__main__':
    parse_tmdb_tables()
    # parse_ny_tables()
