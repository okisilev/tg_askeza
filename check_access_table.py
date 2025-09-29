#!/usr/bin/env python3
"""
Проверка таблицы user_access
"""

import sqlite3

def check_access_table():
    """Проверка таблицы user_access"""
    print("🔍 Проверка таблицы user_access")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('askeza_bot.db')
        cursor = conn.cursor()
        
        # Проверяем структуру таблицы
        cursor.execute("PRAGMA table_info(user_access);")
        columns = cursor.fetchall()
        
        print("📋 Структура таблицы user_access:")
        for col in columns:
            print(f"   • {col[1]} ({col[2]})")
        
        # Проверяем все записи
        cursor.execute('SELECT * FROM user_access WHERE user_id = ?', (760111270,))
        records = cursor.fetchall()
        
        print(f"\n📊 Записи для пользователя 760111270 ({len(records)}):")
        for record in records:
            print(f"   • ID: {record[0]}")
            print(f"     User ID: {record[1]}")
            print(f"     Access Type: {record[2]}")
            print(f"     Created: {record[3]}")
            print(f"     Expires: {record[4]}")
            print(f"     Active: {record[5]}")
            print()
        
        # Проверяем все записи в таблице
        cursor.execute('SELECT * FROM user_access')
        all_records = cursor.fetchall()
        
        print(f"📊 Все записи в таблице ({len(all_records)}):")
        for record in all_records:
            print(f"   • {record[0]} - {record[1]} - {record[2]} - {record[3]} - {record[4]} - {record[5]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    """Основная функция"""
    check_access_table()

if __name__ == "__main__":
    main()
