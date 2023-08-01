import datetime
from faker import Faker
import mysql.connector
import re
import random
from numpy import arange

'''
Methods available:
credit_card()
bank_details()
user()
guest()
host()
wishlist()
properties()
booking()
mappings()
'''

fake = Faker(['de_DE', 'en_US'])
de = fake['de_DE']
Faker.seed(1)


def credit_card():
    insert_stmt = "INSERT INTO `airbnb`.`CreditCard`(`CreditCardType`,`CardHolderName`," \
                  "`SecCode`,`CardNumber`, `ExpiryDate`, `FK_Guest`)" \
                  "VALUES (%s, %s, %s, %s, %s, %s);"

    data = []
    avail_guest = list(range(1, 101))
    for _ in range(100):
        raw = fake.credit_card_full().strip()
        raw = re.sub(r"CVC: |CVV: |CID: ", "", raw)
        item = raw.split("\n")
        card_num, expiry = item[2].split(" ")
        item[2] = item[3]
        item[3] = card_num
        id_guest = random.choice(avail_guest)
        avail_guest.remove(id_guest)
        item.append(expiry)
        item.append(id_guest)

        data.append(item)

    execution(insert_stmt, data)


def bank_details():
    insert_stmt = "INSERT INTO `airbnb`.`BankDetails`(`IBAN`,`BIC`, `BankName`,`FK_idHost`)" \
                  "VALUES (%s, %s, %s, %s);"

    data = []
    avail_host = list(range(1, 101))

    for idx in range(100):
        account = de.iban()
        bic = de.swift(length=11, primary=True, use_dataset=True)
        bank_name = fake.company()
        id_host = random.choice(avail_host)
        avail_host.remove(id_host)
        data.append([
            account,
            bic,
            bank_name,
            id_host,
        ])

    execution(insert_stmt, data)


def user():
    insert_stmt = "INSERT INTO `airbnb`.`User`(`idUser`, `DateOfBirth`,`Email`,`UserPassword`," \
                  "`About`,`Phone`,`ProfilePhotoName`,`ProfilePhoto`,`Address`," \
                  "`FirstName`, `LastName`)" \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"

    data = []
    for idx in range(100):
        id_user = idx + 1
        dob = fake.date_of_birth(minimum_age=18)
        email = fake.company_email()
        password = fake.password(length=12)
        about = fake.paragraph(nb_sentences=3)
        phone = de.phone_number()
        photo_name = fake.text(max_nb_chars=25)
        photo = 'https://loremflickr.com/g/320/240/paris,girl/all'
        address = de.address()
        first_name = de.first_name_nonbinary()
        last_name = de.last_name_nonbinary()

        data.append([
            id_user,
            dob,
            email,
            password,
            about,
            phone,
            photo_name,
            photo,
            address,
            first_name,
            last_name,
        ])

    execution(insert_stmt, data)

    insert_stmt = "INSERT INTO `airbnb`.`EmergencyContact`(`idEmergencyContact`," \
                  "`EmergencyContactName`, `EmergencyContactRelationship`," \
                  "`EmergencyContactPreferredLanguage`, `EmergencyContactEmail`, " \
                  "`EmergencyContactCountry`,`EmergencyContactPhone`,`id_user`)" \
                  "VALUES(%s, %s, %s, %s, %s, %s, %s, %s);"

    data = []
    avail_user = list(range(1, 101))
    for idx in range(100):
        id_emergency = idx + 1
        name = de.name_nonbinary()
        rel = fake.word()
        langs = fake.language_name()
        email = fake.company_email()
        country = fake.country()
        phone = de.phone_number()
        id_user = random.choice(avail_user)
        avail_user.remove(id_user)

        data.append([
            id_emergency,
            name,
            rel,
            langs,
            email,
            country,
            phone,
            id_user,
        ])

    execution(insert_stmt, data)

    insert_stmt = "INSERT INTO `airbnb`.`UserReview`(`idUserReview`,`idHost`,`idGuest`," \
                  "`GuestRating`, `HostRating`,`CommentForHost`,`CommentForGuest`," \
                  "`HostReviewCreated`, `GuestReviewCreated`)" \
                  "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s);"

    data = []
    avail_host = list(range(1, 101))
    avail_guest = list(range(1, 101))
    for idx in range(100):
        id_us_rew = idx + 1
        id_host = random.choice(avail_host)
        avail_host.remove(id_host)
        id_guest = random.choice(avail_guest)
        avail_guest.remove(id_guest)
        g_rate = round(random.uniform(1.0, 5.0), 1)
        h_rate = round(random.uniform(1.0, 5.0), 1)
        comm_4_host = fake.paragraph(nb_sentences=3)
        comm_4_guest = fake.paragraph(nb_sentences=3)
        host_rew_created = fake.date_this_year()
        guest_rew_created = fake.date_this_year()

        data.append([
            id_us_rew,
            id_host,
            id_guest,
            g_rate,
            h_rate,
            comm_4_host,
            comm_4_guest,
            host_rew_created,
            guest_rew_created,
        ])

    execution(insert_stmt, data)

    insert_stmt = "INSERT INTO `airbnb`.`Message` (`idMessage`, `Created`,`Message_To`," \
                  "`Message_From`,`Message`,`id_guest`,`id_host`) VALUES(%s, %s, %s, %s, %s, %s, " \
                  "%s);"

    data = []
    avail_host = list(range(1, 101))
    avail_guest = list(range(1, 101))
    for idx in range(100):
        id_msg = idx + 1
        created = fake.date_this_year()
        message_from = random.choice(avail_host)
        avail_host.remove(message_from)
        message_to = random.choice(avail_guest)
        avail_guest.remove(message_to)
        message = fake.paragraph(nb_sentences=5)
        id_guest = random.randint(1, 100)
        id_host = random.randint(1, 100)

        data.append([
            id_msg,
            created,
            message_from,
            message_to,
            message,
            id_guest,
            id_host,
        ])

    execution(insert_stmt, data)


def guest():
    insert_stmt = "INSERT INTO `airbnb`.`Guest`(`idGuest`,`idUser`,`AverageRating`, " \
                  "`NumberOfRatings`,`idCreditCard`, `GovernmentID`, `YearsOnPlatform`," \
                  "`VerifiedIdentity`, `CurrentResidence`,`SpokenLanguages`)" \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"

    data = []
    available_cc = list(range(1, 101))
    avail_user = list(range(1, 101))
    for idx in range(100):
        id_guest = idx + 1
        id_user = random.choice(avail_user)
        avail_user.remove(id_user)
        rating = round(random.uniform(1.0, 5.0), 1)
        rate_no = random.randint(15, 4950)
        cc = random.choice(available_cc)
        available_cc.remove(cc)
        gov_id = 'https://realpassportgenerator.com/wp-content/uploads/2019/04/German-ID-Card.jpg'
        yop = random.randint(1, 17)
        verified = fake.boolean(chance_of_getting_true=50)
        residence = fake.country()
        langs = fake.language_name()

        data.append([
            id_guest,
            id_user,
            rating,
            rate_no,
            cc,
            gov_id,
            yop,
            verified,
            residence,
            langs,
        ])
    execution(insert_stmt, data)


def host():
    insert_stmt = "INSERT INTO `airbnb`.`Host`(`idHost`,`idUser`,`isSuperHost`, `Rating`, " \
                  "`NumberOfRatings`, `idBankDetails`, `YearsHosting`, `SpokenLanguages`)" \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"

    data = []
    avail_user = list(range(1, 101))
    avail_bank = list(range(1, 101))
    for idx in range(100):
        id_host = idx + 1
        id_user = random.choice(avail_user)
        avail_user.remove(id_user)
        is_super_host = fake.boolean(chance_of_getting_true=50)
        rating = round(random.uniform(1.0, 5.0), 1)
        rate_no = random.randint(15, 4950)
        bank = random.choice(avail_bank)
        avail_bank.remove(bank)
        hosting = random.randint(1, 17)
        langs = fake.language_name()

        data.append([
            id_host,
            id_user,
            is_super_host,
            rating,
            rate_no,
            bank,
            hosting,
            langs,
        ])
    execution(insert_stmt, data)


def wishlist():
    insert_stmt = "INSERT INTO `airbnb`.`Wishlist` (`idWishlist`,`idGuest`,`WishlistName`, " \
                  "`Privacy`) VALUES (%s, %s, %s, %s);"

    data = []
    avail_guest = list(range(1, 101))
    for idx in range(100):
        id_wishlist = idx + 1
        id_guest = random.choice(avail_guest)
        avail_guest.remove(id_guest)
        name = fake.text(max_nb_chars=45)
        privacy = fake.boolean(chance_of_getting_true=50)

        data.append([
            id_wishlist,
            id_guest,
            name,
            privacy,
        ])

    execution(insert_stmt, data)


def properties():
    insert_stmt = "INSERT INTO `airbnb`.`Property` (`idProperty`,`PropertyName`," \
                  "`PropertyDescription`, `PostCode`,`Bathrooms`,`Bedrooms`,`MaxGuestsAllowed`," \
                  "`PricePerNight`,`CleaningFee`, `CheckInTime`,`CheckOutTime`, " \
                  "`IsRefundable`, `CancellationPeriod`,`CancellationType`,`RefundRate`, " \
                  "`NumOfRatings`,`AverageRatings`,`idHost`,`Street`,`StreetNo`,`City`,`Country`," \
                  "`TaxRate`)  VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, " \
                  "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"

    data = []
    avail_bedrooms = list(range(1, 101))
    avail_host = list(range(1, 101))
    for idx in range(100):
        id_prop = idx + 1
        name = fake.text(max_nb_chars=25)
        desc = fake.paragraph(nb_sentences=5)
        post_code = de.postcode()
        bathrooms = random.randint(1, 10)
        bedrooms = random.choice(avail_bedrooms)
        avail_bedrooms.remove(bedrooms)
        max_guests = random.randint(1, 40)
        price = random.uniform(1.00, 9999.00)
        cleaning = random.uniform(1.00, 99.00)
        checkin = fake.date_this_year()
        checkout = fake.date_this_year()
        refundable = fake.boolean(chance_of_getting_true=50)
        cancellation = random.randint(1, 30)
        cancellation_type = fake.text(max_nb_chars=10)
        refund_rate = random.uniform(0.0, 99.9)
        rate_no = random.randint(15, 4950)
        rating = round(random.uniform(1.0, 5.0), 1)
        id_host = random.choice(avail_host)
        avail_host.remove(id_host)
        street = de.street_name()
        str_no = de.building_number()
        city = de.city()
        country = de.country()
        tax_rate = round(random.uniform(0.0, 99.0), 1)

        data.append([
            id_prop,
            name,
            desc,
            post_code,
            bathrooms,
            bedrooms,
            max_guests,
            price,
            cleaning,
            checkin,
            checkout,
            refundable,
            cancellation,
            cancellation_type,
            refund_rate,
            rate_no,
            rating,
            id_host,
            street,
            str_no,
            city,
            country,
            tax_rate,
        ])
    execution(insert_stmt, data)

    insert_stmt = "INSERT INTO `airbnb`.`PropertyPhoto` (`idPhoto`,`idProperty`,`PropertyName`, " \
                  "`ImageFile`) VALUES (%s, %s, %s, %s);"

    data = []
    avail_prop = list(range(1, 101))
    for idx in range(100):
        id_photo = idx + 1
        id_prop = random.choice(avail_prop)
        avail_prop.remove(id_prop)
        name = fake.text(max_nb_chars=45)
        photo = 'https://loremflickr.com/g/320/240/paris,girl/all'

        data.append([
            id_photo,
            id_prop,
            name,
            photo,
        ])

    execution(insert_stmt, data)

    insert_stmt = "INSERT INTO `airbnb`.`PropertyOnWishlist` (`idProperty`,`idGuest`, " \
                  "`idWishlist`,`CheckInDate`,`CheckOutDate`) VALUES (%s, %s, %s, %s, %s);"

    data = []
    avail_prop = list(range(1, 101))
    avail_guest = list(range(1, 101))
    avail_wish = list(range(1, 101))
    for idx in range(100):
        id_prop = random.choice(avail_prop)
        avail_prop.remove(id_prop)
        id_guest = random.choice(avail_guest)
        avail_guest.remove(id_guest)
        id_wish = random.choice(avail_wish)
        avail_wish.remove(id_wish)
        checkin_date = fake.date_this_year()
        checkout_date = fake.date_this_year()

        data.append([
            id_prop,
            id_guest,
            id_wish,
            checkin_date,
            checkout_date,
        ])

    execution(insert_stmt, data)

    insert_stmt = "INSERT INTO `airbnb`.`PropertyReview` (`idPropertyReview`,`idProperty`," \
                  "`idGuest`, `Created_Time`,`CommentInReview`," \
                  "`Cleanliness_Rating`,`Communication_Rating`,`CheckIn_Rating`," \
                  "`Accuracy_Rating`, `Location_Rating`,`Value_Rating`,`Overall_Rating`)" \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"

    data = []
    avail_prop = list(range(1, 101))
    avail_guest = list(range(1, 101))
    for idx in range(100):
        id_rew = idx + 1
        id_prop = random.choice(avail_prop)
        avail_prop.remove(id_prop)
        id_guest = random.choice(avail_guest)
        avail_guest.remove(id_guest)
        created = fake.date_this_year()
        comment = fake.paragraph(nb_sentences=3)
        clean = round(random.uniform(1.0, 5.0), 1)
        comm = round(random.uniform(1.0, 5.0), 1)
        checkin = round(random.uniform(1.0, 5.0), 1)
        accuracy = round(random.uniform(1.0, 5.0), 1)
        location = round(random.uniform(1.0, 5.0), 1)
        value = round(random.uniform(1.0, 5.0), 1)
        overall = round(random.uniform(3.5, 5.0), 1)

        data.append([
            id_rew,
            id_prop,
            id_guest,
            created,
            comment,
            clean,
            comm,
            checkin,
            accuracy,
            location,
            value,
            overall,
        ])

    execution(insert_stmt, data)

    insert_stmt = "INSERT INTO `airbnb`.`PropertyReviewPhoto` (`idGuest`,`idProperty`, " \
                  "`PhotoTitle`, `ImageFile`) VALUES (%s, %s, %s, %s);"

    data = []
    avail_prop = list(range(1, 101))
    avail_guest = list(range(1, 101))
    for idx in range(100):
        id_prop = random.choice(avail_prop)
        avail_prop.remove(id_prop)
        id_guest = random.choice(avail_guest)
        avail_guest.remove(id_guest)
        title = fake.text(max_nb_chars=25)
        photo = 'https://loremflickr.com/g/320/240/paris,girl/all'

        data.append([
            id_prop,
            id_guest,
            title,
            photo,
        ])

    execution(insert_stmt, data)

    insert_stmt = "INSERT INTO `airbnb`.`Bedrooms` (`idProperty`,`BedroomsAvailable`,`BedType`, " \
                  "`Beds`) VALUES (%s, %s, %s, %s);"

    data = []
    avail_prop = list(range(1, 101))
    for idx in range(100):
        id_prop = random.choice(avail_prop)
        avail_prop.remove(id_prop)
        no_bedrooms = []
        for val in arange(1.0, 10.5, 0.5):
            no_bedrooms.append(val)
        bedrooms = random.choice(no_bedrooms)
        bed_type = fake.word()
        beds = random.randint(1, 12)

        data.append([
            id_prop,
            bedrooms,
            bed_type,
            beds,
        ])

    execution(insert_stmt, data)

    insert_stmt = "INSERT INTO `airbnb`.`Amenities`(`idAmenity`,`idProperty`,`AmenityName`) " \
                  "VALUES (%s, %s, %s);"

    data = []
    avail_prop = list(range(1, 101))
    for idx in range(100):
        id_amenity = idx + 1
        id_prop = random.choice(avail_prop)
        avail_prop.remove(id_prop)
        amenity = fake.text(max_nb_chars=25)

        data.append([
            id_amenity,
            id_prop,
            amenity,
        ])

    execution(insert_stmt, data)

    insert_stmt = "INSERT INTO `airbnb`.`HouseRule`(`idRule`,`idProperty`,`RuleName`,  " \
                  "`RuleDetails`) VALUES (%s, %s, %s, %s);"

    data = []
    avail_prop = list(range(1, 101))
    for idx in range(100):
        id_rule = idx + 1
        id_prop = random.choice(avail_prop)
        avail_prop.remove(id_prop)
        rule = fake.text(max_nb_chars=25)
        details = fake.paragraph(nb_sentences=5)

        data.append([
            id_rule,
            id_prop,
            rule,
            details,
        ])

    execution(insert_stmt, data)

    insert_stmt = "INSERT INTO `airbnb`.`Promo`(`idPromo`,`Code`,`Discount_Amt`) VALUES(%s,%s,%s);"

    data = []
    for idx in range(100):
        id_promo = idx + 1
        code = str(fake.nic_handles())
        disc_amt = round(random.uniform(1.00, 999.00), 2)

        data.append([
            id_promo,
            code,
            disc_amt,
        ])

    execution(insert_stmt, data)

    insert_stmt = "INSERT INTO `airbnb`.`Category`(`idCategory`,`CategoryName`) VALUES (%s, %s);"

    data = []
    avail_cat = list(range(1, 101))
    for idx in range(100):
        id_category = random.choice(avail_cat)
        avail_cat.remove(id_category)
        category = fake.word()

        data.append([
            id_category,
            category,
        ])

    execution(insert_stmt, data)

    insert_stmt = "INSERT INTO `airbnb`.`AvailableBookingSlot`(`idProperty`,`StartDate`," \
                  "`EndDate`) VALUES (%s, %s, %s);"

    data = []
    avail_prop = list(range(1, 101))
    for idx in range(100):
        id_prop = random.choice(avail_prop)
        avail_prop.remove(id_prop)
        start_date = fake.date_this_year()
        end_date = start_date + datetime.timedelta(days=10)

        data.append([
            id_prop,
            start_date,
            end_date,
        ])

    execution(insert_stmt, data)


def booking():
    insert_stmt = "INSERT INTO `airbnb`.`Booking`(`idBooking`,`CheckInDate`,`CheckOutDate`," \
                  "`AmountPaid`,`BookingDate`,`SeniorGuests`,`Adults`,`Children`," \
                  "`IsCancelled`,`RefundPaid`,`CancelDate`,`idPromo`,`idGuest`,`idProperty`," \
                  "`TotalPrice`,`Tax`,`TotalPriceWithTax`,`AmountDue`,`RefundAmt`,`MinimumStay`) " \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, " \
                  "%s, %s, %s, %s);"

    data = []
    avail_prop = list(range(1, 101))
    avail_promo = list(range(1, 101))
    avail_guest = list(range(1, 101))
    for idx in range(100):
        id_book = idx + 1
        start_date = fake.date_this_year()
        end_date = start_date + datetime.timedelta(days=10)
        amount_paid = random.randint(300, 9900)
        booked_at = fake.date_this_month()
        seniors = random.randint(0, 5)
        adults = random.randint(0, 4)
        kids = random.randint(0, 5)
        is_cancelled = fake.boolean(chance_of_getting_true=50)
        refunded = fake.boolean(chance_of_getting_true=50)
        cancel_date = fake.date_this_month()
        id_promo = random.choice(avail_promo)
        avail_promo.remove(id_promo)
        id_guest = random.choice(avail_guest)
        avail_guest.remove(id_guest)
        id_prop = random.choice(avail_prop)
        avail_prop.remove(id_prop)
        tot_price = random.randint(900, 9900)
        tax = round(random.uniform(0.0, 99.0), 1)
        price_with_tax = tot_price + tax
        amount_due = price_with_tax - amount_paid
        refund_amt = round(random.uniform(0.0, 9999.0), 2)
        minimum_stay = random.randint(0, 99)

        data.append([
            id_book,
            start_date,
            end_date,
            amount_paid,
            booked_at,
            seniors,
            adults,
            kids,
            is_cancelled,
            refunded,
            cancel_date,
            id_promo,
            id_guest,
            id_prop,
            tot_price,
            tax,
            price_with_tax,
            amount_due,
            refund_amt,
            minimum_stay,
        ])

    execution(insert_stmt, data)


def mappings():
    insert_stmt = "INSERT INTO `airbnb`.`PropertyAmenities`(`idProperty`," \
                  "`idAmenity`) VALUES (%s, %s);"

    data = []
    avail_prop = list(range(1, 101))
    for idx in range(100):
        id_prop = random.choice(avail_prop)
        avail_prop.remove(id_prop)
        avail_amenity = list(range(1, 101))
        for _ in range(1, random.randint(20, 45)):
            id_amen = random.choice(avail_amenity)
            avail_amenity.remove(id_amen)

            data.append([
                id_prop,
                id_amen,
            ])

    execution(insert_stmt, data)

    insert_stmt = "INSERT INTO `airbnb`.`PropertyCategories`(`idProperty`,`idCategory`)  VALUES (" \
                  "%s, %s);"

    data = []
    avail_prop = list(range(1, 101))
    for idx in range(100):
        id_prop = random.choice(avail_prop)
        avail_prop.remove(id_prop)
        avail_categories = list(range(1, 101))
        for _ in range(1, random.randint(6, 16)):
            id_category = random.choice(avail_categories)
            avail_categories.remove(id_category)

            data.append([
                id_prop,
                id_category,
            ])

    execution(insert_stmt, data)


def execution(insert_stmt, data):
    cnx = mysql.connector.connect(user='root',
                                  host='127.0.0.1',
                                  database='airbnb')
    cursor = cnx.cursor()

    try:
        # Executing the SQL command
        print(insert_stmt)
        cursor.execute('SET FOREIGN_KEY_CHECKS = 0;')
        for row in data:
            print(row)
            cursor.execute(insert_stmt, row)
        # Commit your changes in the database
        cursor.execute('SET FOREIGN_KEY_CHECKS = 1;')
        cnx.commit()

        print("Data inserted")

    except Exception as error:
        # Rolling back in case of error
        cnx.rollback()
        print(error)
    # Closing the connection
    cnx.close()


if __name__ == "__main__":
    credit_card()
    bank_details()
    user()
    guest()
    host()
    wishlist()
    properties()
    booking()
    mappings()
