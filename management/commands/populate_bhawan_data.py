import datetime
import random
from decimal import Decimal

import swapper
from django.core.management.base import BaseCommand, CommandError

from base_auth.models import User
from bhawan_app.constants.complaint_items import COMPLAINT_ITEMS
from bhawan_app.models import DefaultItem, Resident
from kernel.constants import biological_information as bio_constants
from shell.constants import residences as residence_constants


class Command(BaseCommand):
    help = (
        "Populate baseline Bhawan app data: residences, default complaint "
        "items, and demo students/residents across bhawans."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be created without writing to the database.",
        )
        parser.add_argument(
            "--students",
            type=int,
            default=50,
            help="Number of demo students/residents to create.",
        )
        parser.add_argument(
            "--password",
            default="pass",
            help="Password for generated demo users.",
        )
        parser.add_argument(
            "--username-prefix",
            default="bhawan_demo",
            help="Prefix used for generated usernames.",
        )

    @staticmethod
    def _build_username(prefix, token):
        max_len = 15
        safe_prefix = "".join(ch for ch in prefix.lower() if ch.isalnum()) or "demo"
        token = "".join(ch for ch in token.lower() if ch.isalnum())
        prefix_len = max_len - len(token)
        if prefix_len < 1:
            return token[-max_len:]
        return f"{safe_prefix[:prefix_len]}{token}"

    def _seed_residences(self, Residence, dry_run):
        created_count = 0
        existing_count = 0

        for code, _label in residence_constants.RESIDENCES:
            exists = Residence.objects.filter(code=code).exists()
            if exists:
                existing_count += 1
                continue

            if not dry_run:
                Residence.objects.create(code=code)
            created_count += 1

        return created_count, existing_count

    def _seed_default_items(self, dry_run):
        created_count = 0
        existing_count = 0

        item_names = [label.strip() for _, label in COMPLAINT_ITEMS]

        for item_name in item_names:
            exists = DefaultItem.objects.filter(name=item_name).exists()
            if exists:
                existing_count += 1
                continue

            if not dry_run:
                DefaultItem.objects.create(name=item_name)
            created_count += 1

        return created_count, existing_count

    def _build_student_profile(self, index):
        # Keep generated demo data deterministic and readable.
        first_names = [
            "Aarav", "Ananya", "Ishaan", "Diya", "Vivaan", "Aditi",
            "Reyansh", "Meera", "Arjun", "Kavya", "Rudra", "Saanvi",
        ]
        last_names = [
            "Sharma", "Verma", "Singh", "Gupta", "Mehta", "Kapoor",
            "Nair", "Iyer", "Das", "Mishra", "Bansal", "Agarwal",
        ]

        first_name = first_names[index % len(first_names)]
        last_name = last_names[(index // len(first_names)) % len(last_names)]
        full_name = f"{first_name} {last_name}"

        age = random.randint(18, 26)
        day_offset = random.randint(0, 364)
        dob = datetime.date.today() - datetime.timedelta(days=(age * 365 + day_offset))

        if index % 2 == 0:
            gender = bio_constants.MAN
            sex = bio_constants.MALE
            pronoun = bio_constants.HE
        else:
            gender = bio_constants.WOMAN
            sex = bio_constants.FEMALE
            pronoun = bio_constants.SHE

        blood_group_codes = [code for code, _ in bio_constants.BLOOD_GROUPS]
        blood_group = blood_group_codes[index % len(blood_group_codes)]

        return {
            "full_name": full_name,
            "short_name": first_name,
            "dob": dob,
            "gender": gender,
            "sex": sex,
            "pronoun": pronoun,
            "blood_group": blood_group,
            "age": age,
        }

    def _seed_students_and_residents(
        self,
        Student,
        Branch,
        Person,
        BiologicalInformation,
        Residence,
        dry_run,
        students_to_create,
        password,
        username_prefix,
    ):
        hostels = list(
            Residence.objects.filter(
                code__in=[code for code, _ in residence_constants.BOYS_HOSTELS + residence_constants.GIRLS_HOSTELS]
            )
        )
        if not hostels:
            raise CommandError("No hostel residences found. Seed residences first.")

        branch = Branch.objects.order_by("id").first()
        if branch is None:
            raise CommandError("No Branch found. Create branch data before seeding students.")

        max_enrolment = 12000000
        existing_enrolments = Student.objects.values_list("enrolment_number", flat=True)
        for enrol in existing_enrolments:
            try:
                max_enrolment = max(max_enrolment, int(enrol))
            except (TypeError, ValueError):
                continue

        created_students = 0
        skipped_students = 0

        for i in range(1, students_to_create + 1):
            username = self._build_username(username_prefix, f"{i:05d}")
            user_exists = User.objects.filter(username=username).exists()

            if user_exists:
                skipped_students += 1
                continue

            if dry_run:
                created_students += 1
                continue

            profile = self._build_student_profile(i)
            user = User.objects.create(username=username)
            user.set_password(password)
            user.save()

            person = Person.objects.create(
                user=user,
                full_name=profile["full_name"],
                short_name=profile["short_name"],
            )

            max_enrolment += 1
            current_semester = random.randint(1, 8)
            student = Student.objects.create(
                person=person,
                branch=branch,
                start_date=datetime.date.today() - datetime.timedelta(days=random.randint(30, 900)),
                current_semester=current_semester,
                current_cgpa=Decimal(str(random.uniform(6.0, 9.8))).quantize(Decimal("0.001")),
                enrolment_number=str(max_enrolment),
            )

            BiologicalInformation.objects.update_or_create(
                person=person,
                defaults={
                    "date_of_birth": profile["dob"],
                    "blood_group": profile["blood_group"],
                    "gender": profile["gender"],
                    "sex": profile["sex"],
                    "pronoun": profile["pronoun"],
                    "impairment": bio_constants.NO_IMPAIRMENT,
                },
            )

            hostel = random.choice(hostels)
            room_number = f"{random.randint(100, 499)}"
            Resident.objects.create(
                person=person,
                hostel=hostel,
                room_number=room_number,
                fee_type="liv",
                is_living_in_campus=True,
                address_bhawan=f"Room {room_number}, {hostel.name}",
                admission_date=datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 1200)),
                contact_number_as_bhawan=f"98{random.randint(10000000, 99999999)}",
            )

            created_students += 1

        return created_students, skipped_students

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        students_to_create = options["students"]
        password = options["password"]
        username_prefix = options["username_prefix"]

        if students_to_create < 0:
            raise CommandError("--students must be >= 0")

        Branch = swapper.load_model("kernel", "Branch")
        Student = swapper.load_model("kernel", "Student")
        Person = swapper.load_model("kernel", "Person")
        Residence = swapper.load_model("kernel", "Residence")
        BiologicalInformation = swapper.load_model("kernel", "BiologicalInformation")

        residence_created, residence_existing = self._seed_residences(
            Residence=Residence,
            dry_run=dry_run,
        )
        default_item_created, default_item_existing = self._seed_default_items(
            dry_run=dry_run,
        )

        student_created, student_skipped = self._seed_students_and_residents(
            Student=Student,
            Branch=Branch,
            Person=Person,
            BiologicalInformation=BiologicalInformation,
            Residence=Residence,
            dry_run=dry_run,
            students_to_create=students_to_create,
            password=password,
            username_prefix=username_prefix,
        )

        mode = "DRY RUN" if dry_run else "APPLIED"
        self.stdout.write(
            f"[{mode}] Residences -> created: {residence_created}, existing: {residence_existing}"
        )
        self.stdout.write(
            f"[{mode}] Default items -> created: {default_item_created}, existing: {default_item_existing}"
        )
        self.stdout.write(
            f"[{mode}] Students/Residents -> created: {student_created}, skipped(existing username): {student_skipped}"
        )
