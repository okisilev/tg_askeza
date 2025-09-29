#!/usr/bin/env python3
"""
Проверка статуса пользователя 760111270
"""

import sqlite3
from datetime import datetime

def check_user_status():
    """Проверка статуса пользователя"""
    print("🔍 Проверка статуса пользователя 760111270")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('askeza_bot.db')
        cursor = conn.cursor()
        
        # Проверяем пользователя
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (760111270,))
        user = cursor.fetchone()
        
        if user:
            print(f"✅ Пользователь найден:")
            print(f"   • ID: {user[0]}")
            print(f"   • Username: {user[1]}")
            print(f"   • First name: {user[2]}")
            print(f"   • Last name: {user[3]}")
            print(f"   • Created: {user[4]}")
            print(f"   • Active: {user[5]}")
        else:
            print("❌ Пользователь не найден")
            return False
        
        # Проверяем платежи
        cursor.execute('''
            SELECT yookassa_payment_id, payment_type, amount, status, created_at 
            FROM payments 
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (760111270,))
        payments = cursor.fetchall()
        
        print(f"\n💳 Платежи ({len(payments)}):")
        for payment in payments:
            print(f"   • {payment[0]} - {payment[1]} - {payment[2]}₽ - {payment[3]} - {payment[4]}")
        
        # Проверяем доступ
        cursor.execute('''
            SELECT access_type, created_at, expires_at, is_active 
            FROM user_access 
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (760111270,))
        access_records = cursor.fetchall()
        
        print(f"\n🔐 Доступ ({len(access_records)}):")
        for access in access_records:
            print(f"   • {access[0]} - {access[1]} - {access[2]} - {access[3]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    """Основная функция"""
    check_user_status()

if __name__ == "__main__":
    main()
