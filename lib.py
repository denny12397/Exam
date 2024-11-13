import json
import sqlite3
import os
from typing import List

def connect_db(db_path: str) -> sqlite3.Connection:
    """連接到 SQLite 資料庫，若不存在則創建"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # 使用字典型結果
        return conn
    except sqlite3.DatabaseError as e:
        print(f"資料庫錯誤: {e}")
        raise

def create_table(db_path: str):
    """建立電影資料表"""
    try:
        conn = connect_db(db_path)
        with conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS movies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    director TEXT NOT NULL,
                    genre TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    rating REAL
                )
            ''')
        print("電影資料表建立成功")
    except Exception as e:
        print(f"建立資料表時發生錯誤: {e}")

def import_movies(db_path: str, json_path: str):
    if not os.path.exists(db_path) :
        print("資料庫未建立。")
        print("建立資料庫中....")
        create_table(db_path)
        print("資料庫建立完成！")

    """從 JSON 檔案匯入電影資料到資料庫"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            movies = json.load(f)

        conn = connect_db(db_path)
        with conn:
            for movie in movies:
                conn.execute('''
                    INSERT INTO movies (title, director, genre, year, rating)
                    VALUES (?, ?, ?, ?, ?)
                ''', (movie['title'], movie['director'], movie['genre'], movie['year'], movie['rating']))
        print("電影已匯入")
    except FileNotFoundError:
        print("找不到電影資料檔")
    except json.JSONDecodeError:
        print("讀取 JSON 檔案錯誤")
    except sqlite3.DatabaseError as e:
        print(f"資料庫錯誤: {e}")

def search_movies(db_path: str):
    if not os.path.exists(db_path) :
        print("資料庫未建立。")
        print("建立資料庫中....")
        create_table(db_path)
        print("資料庫建立完成！")

    """查詢電影資料"""
    try:
        conn = connect_db(db_path)
        cursor = conn.cursor()

        choice = input("查詢全部電影嗎？(y/n): ")
        if choice.lower() == 'y':
            cursor.execute("SELECT * FROM movies")
        else:
            movie_title = input("請輸入電影名稱: ")
            cursor.execute("SELECT * FROM movies WHERE title LIKE ?", ('%' + movie_title + '%',))

        movies = cursor.fetchall()
        if not movies:
            print("查無資料")
        else:
            print(f"{'電影名稱':<20}{'導演':<20}{'類型':<10}{'上映年份':<10}{'評分':<5}")
            print("-" * 70)
            for movie in movies:
                print(f"{movie['title']:<20}{movie['director']:<20}{movie['genre']:<10}{movie['year']:<10}{movie['rating']:<5}")
    except Exception as e:
        print(f"查詢電影時發生錯誤: {e}")

def add_movie(db_path: str):
    if not os.path.exists(db_path) :
        print("資料庫未建立。")
        print("建立資料庫中....")
        create_table(db_path)
        print("資料庫建立完成！")

    """新增電影資料"""
    try:
        title = input("電影名稱: ")
        director = input("導演: ")
        genre = input("類型: ")
        year = int(input("上映年份: "))
        rating = float(input("評分 (1.0 - 10.0): "))
        conn = connect_db(db_path)
        with conn:
            conn.execute('''
                INSERT INTO movies (title, director, genre, year, rating)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, director, genre, year, rating))
        print("電影已新增")
    except ValueError:
        print("請輸入有效的數字格式")
    except sqlite3.DatabaseError as e:
        print(f"資料庫錯誤: {e}")

def modify_movie(db_path: str):
    if not os.path.exists(db_path) :
        print("資料庫未建立。")
        print("建立資料庫中....")
        create_table(db_path)
        print("資料庫建立完成！")
    else :
        """修改電影資料"""
        try:
            movie_title = input("請輸入要修改的電影名稱: ")

            conn = connect_db(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM movies WHERE title LIKE ?", ('%' + movie_title + '%',))
            movie = cursor.fetchone()

            if not movie:
                print("找不到電影")
                return
            print(f"{'電影名稱':<20}{'導演':<20}{'類型':<10}{'上映年份':<10}{'評分':<5}")
            print("-" * 70)
            print(f"{movie['title']:<20}{movie['director']:<20}{movie['genre']:<10}{movie['year']:<10}{movie['rating']:<5}")

            new_title = input("請輸入新的電影名稱 (若不修改請直接按 Enter): ") or movie['title']
            new_director = input("請輸入新的導演 (若不修改請直接按 Enter): ") or movie['director']
            new_genre = input("請輸入新的類型 (若不修改請直接按 Enter): ") or movie['genre']
            new_year = input("請輸入新的上映年份 (若不修改請直接按 Enter): ")
            new_rating = input("請輸入新的評分 (若不修改請直接按 Enter): ")

            new_year = int(new_year) if new_year else movie['year']
            new_rating = float(new_rating) if new_rating else movie['rating']

            with conn:
                conn.execute('''
                    UPDATE movies
                    SET title = ?, director = ?, genre = ?, year = ?, rating = ?
                    WHERE id = ?
                ''', (new_title, new_director, new_genre, new_year, new_rating, movie['id']))
            print("資料已修改")
        except ValueError:
            print("請輸入有效的數字格式")
        except sqlite3.DatabaseError as e:
            print(f"資料庫錯誤: {e}")

def delete_movies(db_path: str):
    if not os.path.exists(db_path) :
        print("資料庫未建立。")
        print("建立資料庫中....")
        create_table(db_path)
        print("資料庫建立完成！")
    else:
        """刪除電影資料"""
        try:
            conn = connect_db(db_path)
            cursor = conn.cursor()

            choice = input("刪除全部電影嗎？(y/n): ")
            if choice.lower() == 'y':
                with conn:
                    conn.execute("DELETE FROM movies")
                print("所有電影已刪除")
            else:
                movie_title = input("請輸入要刪除的電影名稱: ")
                cursor.execute("SELECT * FROM movies WHERE title LIKE ?", ('%' + movie_title + '%',))
                movies = cursor.fetchall()
                if not movies:
                    print("查無電影")
                    return

                for movie in movies:
                    print(f"{movie['title']}, {movie['director']}, {movie['genre']}, {movie['year']}, {movie['rating']}")

                delete_confirm = input("是否要刪除(y/n): ")
                if delete_confirm.lower() == 'y':
                    with conn:
                        conn.execute("DELETE FROM movies WHERE id = ?", (movies[0]['id'],))  # 假設刪除第一個匹配的電影
                    print("電影已刪除")
        except sqlite3.DatabaseError as e:
            print(f"資料庫錯誤: {e}")

def export_movies(db_path: str, json_out_path: str):
    if not os.path.exists(db_path) :
        print("資料庫未建立。")
        print("建立資料庫中....")
        create_table(db_path)
        print("資料庫建立完成！")

    else:
        """匯出電影資料到 JSON 檔案"""
        try:
            conn = connect_db(db_path)
            cursor = conn.cursor()
            export_all = input("匯出全部電影嗎？(y/n) ：")

            if export_all == "y":
                cursor.execute("SELECT * FROM movies")
            elif export_all == "n" :
                movie_title = input("請輸入要匯出的電影名稱: ")
                cursor.execute("SELECT * FROM movies WHERE title LIKE ?", ('%' + movie_title + '%',))

            movies = cursor.fetchall()

            if not movies:
                print("查無電影")
                return

            with open(json_out_path, 'w', encoding='utf-8') as f:
                json.dump([dict(movie) for movie in movies], f, ensure_ascii=False, indent=4)

            print("電影資料已匯出至", json_out_path)
        except sqlite3.DatabaseError as e:
            print(f"資料庫錯誤: {e}")