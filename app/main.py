from __future__ import annotations

import argparse
from datetime import date
from decimal import Decimal

from emotion_tracker_db.crud import create_emotion_record, create_user, list_emotion_records, list_users
from emotion_tracker_db.db import create_database, create_tables, get_session


def cmd_init_db(_: argparse.Namespace) -> None:
    create_database()
    create_tables()
    print("PostgreSQL database and tables are ready.")


def cmd_create_user(args: argparse.Namespace) -> None:
    with get_session() as session:
        user = create_user(
            session=session,
            email=args.email,
            password_hash=args.password_hash,
            timezone=args.timezone,
        )
        print(f"User created: id={user.id}, email={user.email}")


def cmd_list_users(_: argparse.Namespace) -> None:
    with get_session() as session:
        users = list_users(session)
        if not users:
            print("No users found.")
            return
        for user in users:
            print(f"{user.id} | {user.email} | {user.timezone} | {user.status.value}")


def cmd_add_emotion_record(args: argparse.Namespace) -> None:
    with get_session() as session:
        record = create_emotion_record(
            session=session,
            user_id=args.user_id,
            record_date=date.fromisoformat(args.record_date),
            mood=args.mood,
            anxiety=args.anxiety,
            fatigue=args.fatigue,
            sleep_hours=Decimal(args.sleep_hours) if args.sleep_hours is not None else None,
            note=args.note,
        )
        print(f"Emotion record created: id={record.id}, user_id={record.user_id}, record_date={record.record_date}")


def cmd_list_emotion_records(args: argparse.Namespace) -> None:
    with get_session() as session:
        records = list_emotion_records(session, args.user_id)
        if not records:
            print("No emotion records found.")
            return
        for record in records:
            print(
                f"{record.id} | {record.record_date} | mood={record.mood} | "
                f"anxiety={record.anxiety} | fatigue={record.fatigue} | sleep={record.sleep_hours}"
            )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Emotion tracker database management.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_db_parser = subparsers.add_parser("init-db", help="Create all database tables.")
    init_db_parser.set_defaults(func=cmd_init_db)

    create_user_parser = subparsers.add_parser("create-user", help="Create a new user.")
    create_user_parser.add_argument("--email", required=True)
    create_user_parser.add_argument("--password-hash", required=True)
    create_user_parser.add_argument("--timezone", required=True)
    create_user_parser.set_defaults(func=cmd_create_user)

    list_users_parser = subparsers.add_parser("list-users", help="List all users.")
    list_users_parser.set_defaults(func=cmd_list_users)

    add_record_parser = subparsers.add_parser("add-emotion-record", help="Add a daily emotion record.")
    add_record_parser.add_argument("--user-id", required=True)
    add_record_parser.add_argument("--record-date", required=True, help="Date in YYYY-MM-DD format.")
    add_record_parser.add_argument("--mood", required=True, type=int)
    add_record_parser.add_argument("--anxiety", required=True, type=int)
    add_record_parser.add_argument("--fatigue", required=True, type=int)
    add_record_parser.add_argument("--sleep-hours")
    add_record_parser.add_argument("--note")
    add_record_parser.set_defaults(func=cmd_add_emotion_record)

    list_records_parser = subparsers.add_parser("list-emotion-records", help="List emotion records for a user.")
    list_records_parser.add_argument("--user-id", required=True)
    list_records_parser.set_defaults(func=cmd_list_emotion_records)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
