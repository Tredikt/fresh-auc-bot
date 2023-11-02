from get_bot_and_db import get_bot_and_db


def winner_places(code, text=None, winner=None):
    bot, db = get_bot_and_db()
    users = db.get_bid(code)
    max_bids = list()
    usernames = list()

    # print(f"{users =}")
    if len(users) > 0:
        for num in range(-100, 0, -1):
            try:
                if users[num][1] == users[num - 1][1]:
                    users.remove(users[-2])
            except IndexError:
                continue

        if len(users) > 0:
            for _ in range(4):
                try:
                    maximum = max(users, key=lambda x: x[2])[1]
                except ValueError:
                    break

                # print(f"{maximum = } {usernames = }")
                if maximum not in usernames:
                    usernames.append(maximum)
                    max_bids.append(max(users, key=lambda x: x[2]))
                    for e in users:
                        # print("eee", e[1], maximum, users)
                        if e[1] == maximum:
                            users.remove(e)

        # print(f"{usernames =}, {max_bids =}")
        # print(sorted(max_bids, key=lambda x: x[2], reverse=True))
        winners = sorted(max_bids, key=lambda x: x[2], reverse=True)
        # print(f"{winners =}")
        if winner:
            fp = list(winners[0][1])
            fp[-1] = "*"
            fp[-2] = "*"
            first_place = "".join(fp)

            winner_text = f"🥇 {first_place} {winners[0][2]}\n"

            return winner_text

        elif text:
            if len(winners) == 3:
                fp = list(winners[0][1])
                fp[-1] = "*"
                fp[-2] = "*"
                first_place = "".join(fp)
                sp = list(winners[1][1])
                sp[-1] = "*"
                sp[-2] = "*"
                second_place = "".join(sp)
                tp = list(winners[2][1])
                tp[-1] = "*"
                tp[-2] = "*"
                third_place = "".join(tp)
                winner_text = f"🥇 {first_place} {winners[0][2]}\n" \
                               f"🥈 {second_place} {winners[1][2]}\n" \
                               f"🥉 {third_place} {winners[2][2]}\n"

                return winner_text

            elif len(winners) == 2:
                fp = list(winners[0][1])
                fp[-1] = "*"
                fp[-2] = "*"
                first_place = "".join(fp)
                sp = list(winners[1][1])
                sp[-1] = "*"
                sp[-2] = "*"
                second_place = "".join(sp)
                winner_text = f"🥇 {first_place} {winners[0][2]}\n" \
                               f"🥈 {second_place} {winners[1][2]}\n"

                return winner_text

            elif len(winners) == 1:
                print(winners)
                fp = list(winners[0][1])
                fp[-1] = "*"
                fp[-2] = "*"
                first_place = "".join(fp)

                winner_text = f"🥇 {first_place} {winners[0][2]}\n"

                return winner_text

            else:
                return None

        return winners
    return ""