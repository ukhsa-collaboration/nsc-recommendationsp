"""
Scraper extracting the list of NSC policies from the legacy web site.

"""

import json

from nsc.contact.models import Contact
from nsc.policy.models import Policy
from nsc.stakeholder.models import Stakeholder
from nsc.subscription.models import Subscription


OLD_TYPE_MAPPING = {
    "10": Stakeholder.TYPE_PATIENT_GROUP,
    "20": Stakeholder.TYPE_PROFESSIONAL,
    "30": Stakeholder.TYPE_PROFESSIONAL,
    "40": Stakeholder.TYPE_INDIVIDUAL,
    "50": Stakeholder.TYPE_OTHER,
}

OLD_REGION_MAPPING = {
    "10": Stakeholder.COUNTRY_ENGLAND,
    "20": Stakeholder.COUNTRY_SCOTLAND,
    "30": Stakeholder.COUNTRY_NORTHERN_IRELAND,
    "40": Stakeholder.COUNTRY_WALES,
    "50": Stakeholder.COUNTRY_UK,
    "60": Stakeholder.COUNTRY_INTERNATIONAL,
}


def run():
    print("Scraping...")

    import_db_dump()

    print("Finished")


def import_db_dump():
    Stakeholder.objects.all().delete()
    Subscription.objects.all().delete()

    policy_name_mapping = dict(Policy.objects.all().values_list("name", "id"))

    with open("fixtures/MergedStakeholders.json") as f:
        raw = json.load(f)

    for entry in raw:
        policies = [find_policy_id(name, policy_name_mapping) for name in entry["SH_Policies"]]

        if entry["SH_Is_subscriber"] == "Y":
            create_subscriber(entry, policies)
        else:
            create_stakeholder(entry, policies)


def find_policy_id(name, mapping):
    match = mapping.get(name)
    if match is None:
        print(f"Could not find a policy '{name}'")

    return match


def create_subscriber(raw_entry, policies):
    sub = Subscription.objects.get_or_create(email=raw_entry["SH_Contact_email"])[0]
    sub.policies.set(set(sub.policies.values_list('id', flat=True)) | {p for p in policies if p})


def create_stakeholder(raw_entry, policies):
    stakeholder = Stakeholder.objects.get_or_create(
        name=raw_entry["SH_Name"],
        type=OLD_TYPE_MAPPING[raw_entry["SH_Type"]],
        countries=[OLD_REGION_MAPPING[raw_entry["SH_Region"]]],
        url=raw_entry["SH_Website"],
        is_public=raw_entry["SH_Public"] == "Y",
        comments=raw_entry["SH_UK_NSC_notes"],
    )[0]
    stakeholder.policies.set(set(stakeholder.policies.values_list('id', flat=True)) | {p for p in policies if p})

    if any([
        raw_entry["SH_Contact_name"],
        raw_entry["SH_Contact_position"],
        raw_entry["SH_Contact_email"],
        raw_entry["SH_Contact_phone"],
    ]):
        Contact.objects.create(
            stakeholder=stakeholder,
            name=raw_entry["SH_Contact_name"],
            role=raw_entry["SH_Contact_position"],
            email=raw_entry["SH_Contact_email"],
            phone=raw_entry["SH_Contact_phone"],
        )

    if any([
        raw_entry["SH_Secondary_contact_name"],
        raw_entry["SH_Secondary_contact_position"],
        raw_entry["SH_Secondary_contact_email"],
        raw_entry["SH_Secondary_contact_phone"],
    ]):
        Contact.objects.create(
            stakeholder=stakeholder,
            name=raw_entry["SH_Secondary_contact_name"],
            role=raw_entry["SH_Secondary_contact_position"],
            email=raw_entry["SH_Secondary_contact_email"],
            phone=raw_entry["SH_Secondary_contact_phone"],
        )
