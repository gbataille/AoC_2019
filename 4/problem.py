def get_inputs():
    with open("input.csv") as f:
        return f.read()

def get_min_max(in_string):
    return in_string.split('-')


def meet_criteria(num):
    num_str = str(num)
    if len(num_str) != 6:
        return False

    count_c = {}
    last_c = -1
    for c in num_str:
        int_c = int(c)
        if int_c < last_c:
            return False

        if c in count_c:
            count_c[c] = count_c[c] + 1
        else:
            count_c[c] = 1

        last_c = int_c

    for key, value in count_c.items():
        if value == 2:
            return True

    return False


in_string = get_inputs()
min_bound, max_bound = get_min_max(in_string)

print(min_bound)
print(max_bound)

valid_passwords = []
for num in range(int(min_bound), int(max_bound)):
    if meet_criteria(num):
        valid_passwords.append(num)

print(valid_passwords)
print(len(valid_passwords))
