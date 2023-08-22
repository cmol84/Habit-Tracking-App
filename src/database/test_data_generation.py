

def generate_test_data():
    # iterate through a random amount - done
    # generate names, periodicity and list of tasks - done
    testdata_list_habits = []
    for _ in range(10):
        name = fake.word()
        periods = ([Periodicity.DAILY, Periodicity.WEEKLY, Periodicity.MONTHLY])
        periodicity = random.choice(periods)
        task_list = fake.texts(nb_texts=5, max_nb_chars=40)
        testdata_list_habits.append([
            name,
            periodicity,
            task_list
        ])
