from get_bot_and_db import get_bot_and_db


def winner_places(code, text=None, winner=None):
    bot, db = get_bot_and_db()
    users = db.get_bid(code)
    max_bids = list()
    usernames = list()

    if len(users) > 0:
        for _ in range(4):
            if len(users) > 0:
                if max(users, key=lambda x: x[2])[1] not in usernames:
                    usernames.append(max(users, key=lambda x: x[2])[1])
                    max_bids.append(max(users, key=lambda x: x[2]))
                    for e in users:
                        if e[1] == max(users, key=lambda x: x[2])[1]:
                            users.remove(e)

        # print(usernames, max_bids)
        # print(sorted(max_bids, key=lambda x: x[2], reverse=True))
        winners = sorted(max_bids, key=lambda x: x[2], reverse=True)

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