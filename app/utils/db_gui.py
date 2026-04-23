from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from tkinter import END, BOTH, LEFT, RIGHT, X, Y, Button, Entry, Frame, Label, LabelFrame, Listbox, Scrollbar, StringVar, Text, Tk, Toplevel, messagebox
from tkinter.ttk import Combobox

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models import UserStatus
from app.repositories import EmotionRecordRepository, UserHobbyRepository, UserRepository


class DatabaseGui:
    def __init__(self) -> None:
        self.root = Tk()
        self.root.title("Emotion Tracker DB GUI")
        self.root.geometry("1200x700")

        self.db = SessionLocal()
        self.user_repo = UserRepository(self.db)
        self.hobby_repo = UserHobbyRepository(self.db)
        self.emotion_repo = EmotionRecordRepository(self.db)

        self.selected_user_id = None
        self.selected_user_label = StringVar(value="User not selected")

        self._build_layout()
        self.refresh_users()

    def _build_layout(self) -> None:
        main_frame = Frame(self.root, padx=12, pady=12)
        main_frame.pack(fill=BOTH, expand=True)

        left_frame = Frame(main_frame)
        left_frame.pack(side=LEFT, fill=Y, padx=(0, 12))

        center_frame = Frame(main_frame)
        center_frame.pack(side=LEFT, fill=BOTH, expand=True)

        right_frame = Frame(main_frame)
        right_frame.pack(side=RIGHT, fill=BOTH, expand=True)

        self._build_user_creation(left_frame)
        self._build_user_list(left_frame)
        self._build_hobby_panel(center_frame)
        self._build_emotion_panel(right_frame)

    def _build_user_creation(self, parent: Frame) -> None:
        frame = LabelFrame(parent, text="Create User", padx=10, pady=10)
        frame.pack(fill=X, pady=(0, 12))

        Label(frame, text="Email").pack(anchor="w")
        self.email_entry = Entry(frame, width=35)
        self.email_entry.pack(fill=X, pady=(0, 8))

        Label(frame, text="Password hash").pack(anchor="w")
        self.password_hash_entry = Entry(frame, width=35)
        self.password_hash_entry.pack(fill=X, pady=(0, 8))

        Label(frame, text="Timezone").pack(anchor="w")
        self.timezone_entry = Entry(frame, width=35)
        self.timezone_entry.insert(0, "Europe/Moscow")
        self.timezone_entry.pack(fill=X, pady=(0, 8))

        Label(frame, text="Status").pack(anchor="w")
        self.status_combo = Combobox(
            frame,
            values=[status.value for status in UserStatus],
            state="readonly",
            width=32,
        )
        self.status_combo.set(UserStatus.ACTIVE.value)
        self.status_combo.pack(fill=X, pady=(0, 8))

        Button(frame, text="Create user", command=self.create_user).pack(fill=X)

    def _build_user_list(self, parent: Frame) -> None:
        frame = LabelFrame(parent, text="Users", padx=10, pady=10)
        frame.pack(fill=BOTH, expand=True)

        self.users_listbox = Listbox(frame, width=42, height=25)
        self.users_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        self.users_listbox.bind("<<ListboxSelect>>", self.on_user_select)

        scrollbar = Scrollbar(frame, command=self.users_listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.users_listbox.config(yscrollcommand=scrollbar.set)

        Button(parent, text="Refresh users", command=self.refresh_users).pack(fill=X, pady=(8, 0))

    def _build_hobby_panel(self, parent: Frame) -> None:
        header = LabelFrame(parent, text="Hobbies", padx=10, pady=10)
        header.pack(fill=BOTH, expand=True)

        Label(header, textvariable=self.selected_user_label).pack(anchor="w", pady=(0, 8))

        Label(header, text="New hobby").pack(anchor="w")
        self.hobby_entry = Entry(header, width=40)
        self.hobby_entry.pack(fill=X, pady=(0, 8))

        Button(header, text="Add hobby", command=self.add_hobby).pack(fill=X, pady=(0, 8))

        self.hobbies_listbox = Listbox(header, height=20)
        self.hobbies_listbox.pack(fill=BOTH, expand=True)

        Button(header, text="Refresh hobbies", command=self.refresh_hobbies).pack(fill=X, pady=(8, 0))

    def _build_emotion_panel(self, parent: Frame) -> None:
        frame = LabelFrame(parent, text="Emotion Records", padx=10, pady=10)
        frame.pack(fill=BOTH, expand=True)

        Label(frame, textvariable=self.selected_user_label).pack(anchor="w", pady=(0, 8))

        form = Frame(frame)
        form.pack(fill=X)

        self.record_date_entry = self._labeled_entry(form, "Date", "2026-04-14")
        self.mood_entry = self._labeled_entry(form, "Mood", "7")
        self.anxiety_entry = self._labeled_entry(form, "Anxiety", "4")
        self.fatigue_entry = self._labeled_entry(form, "Fatigue", "5")
        self.sleep_entry = self._labeled_entry(form, "Sleep hours", "7.5")

        Label(frame, text="Note").pack(anchor="w", pady=(8, 0))
        self.note_text = Text(frame, height=4)
        self.note_text.pack(fill=X, pady=(0, 8))

        Button(frame, text="Add emotion record", command=self.add_emotion_record).pack(fill=X, pady=(0, 8))

        self.records_listbox = Listbox(frame, height=18)
        self.records_listbox.pack(fill=BOTH, expand=True)

        Button(frame, text="Refresh records", command=self.refresh_records).pack(fill=X, pady=(8, 0))

    def _labeled_entry(self, parent: Frame, label: str, default: str) -> Entry:
        Label(parent, text=label).pack(anchor="w")
        entry = Entry(parent, width=40)
        entry.insert(0, default)
        entry.pack(fill=X, pady=(0, 6))
        return entry

    def refresh_users(self) -> None:
        self.users_listbox.delete(0, END)
        users = self.user_repo.list()
        self._users_cache = users

        for user in users:
            self.users_listbox.insert(END, f"{user.email} | {user.timezone} | {user.status.value}")

    def on_user_select(self, _: object) -> None:
        selection = self.users_listbox.curselection()
        if not selection:
            return

        user = self._users_cache[selection[0]]
        self.selected_user_id = user.id
        self.selected_user_label.set(f"Selected: {user.email} ({user.id})")
        self.refresh_hobbies()
        self.refresh_records()

    def create_user(self) -> None:
        email = self.email_entry.get().strip()
        password_hash = self.password_hash_entry.get().strip()
        timezone = self.timezone_entry.get().strip()
        status = self.status_combo.get().strip()

        if not email or not password_hash or not timezone:
            messagebox.showerror("Validation error", "Email, password hash and timezone are required.")
            return

        try:
            self.user_repo.create(
                obj_in={
                    "email": email,
                    "password_hash": password_hash,
                    "timezone": timezone,
                    "status": UserStatus(status),
                }
            )
            self.db.commit()
        except Exception as exc:
            self.db.rollback()
            messagebox.showerror("Create user failed", str(exc))
            return

        self.email_entry.delete(0, END)
        self.password_hash_entry.delete(0, END)
        self.timezone_entry.delete(0, END)
        self.timezone_entry.insert(0, "Europe/Moscow")
        self.status_combo.set(UserStatus.ACTIVE.value)
        self.refresh_users()
        messagebox.showinfo("Success", "User created.")

    def add_hobby(self) -> None:
        if self.selected_user_id is None:
            messagebox.showwarning("No user", "Select a user first.")
            return

        hobby = self.hobby_entry.get().strip()
        if not hobby:
            messagebox.showerror("Validation error", "Hobby is required.")
            return

        try:
            self.hobby_repo.add(user_id=self.selected_user_id, hobby=hobby)
            self.db.commit()
        except Exception as exc:
            self.db.rollback()
            messagebox.showerror("Add hobby failed", str(exc))
            return

        self.hobby_entry.delete(0, END)
        self.refresh_hobbies()
        messagebox.showinfo("Success", "Hobby added.")

    def add_emotion_record(self) -> None:
        if self.selected_user_id is None:
            messagebox.showwarning("No user", "Select a user first.")
            return

        try:
            record_date = date.fromisoformat(self.record_date_entry.get().strip())
            mood = int(self.mood_entry.get().strip())
            anxiety = int(self.anxiety_entry.get().strip())
            fatigue = int(self.fatigue_entry.get().strip())
            sleep_raw = self.sleep_entry.get().strip()
            sleep_hours = Decimal(sleep_raw) if sleep_raw else None
        except (ValueError, InvalidOperation) as exc:
            messagebox.showerror("Validation error", f"Invalid input: {exc}")
            return

        note = self.note_text.get("1.0", END).strip() or None

        try:
            self.emotion_repo.create(
                user_id=self.selected_user_id,
                record_date=record_date,
                mood=mood,
                anxiety=anxiety,
                fatigue=fatigue,
                sleep_hours=sleep_hours,
                note=note,
            )
            self.db.commit()
        except Exception as exc:
            self.db.rollback()
            messagebox.showerror("Add emotion record failed", str(exc))
            return

        self.note_text.delete("1.0", END)
        self.refresh_records()
        messagebox.showinfo("Success", "Emotion record added.")

    def refresh_hobbies(self) -> None:
        self.hobbies_listbox.delete(0, END)
        if self.selected_user_id is None:
            return

        hobbies = self.hobby_repo.list_by_user(self.selected_user_id)

        for hobby in hobbies:
            self.hobbies_listbox.insert(END, f"{hobby.hobby} | {hobby.created_at}")

    def refresh_records(self) -> None:
        self.records_listbox.delete(0, END)
        if self.selected_user_id is None:
            return

        records = self.emotion_repo.list_by_user(self.selected_user_id)

        for record in records:
            self.records_listbox.insert(
                END,
                f"{record.record_date} | mood={record.mood} anxiety={record.anxiety} "
                f"fatigue={record.fatigue} sleep={record.sleep_hours} note={record.note or ''}",
            )

    def run(self) -> None:
        self.root.mainloop()


def run_db_gui() -> None:
    DatabaseGui().run()
