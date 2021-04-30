if __name__ == '__main__':
    import requests

    # upload user stats (skill and sessions)

    # wait for player goal to be created (while loop with get request until we get data?)
    # create goal on guide side and put completed=false, performance, target and score information

    # wait for session goal to be created
    # create session goal on guide side and put completed=false, performance information (from last session)

    # loop until session goal == completed

    #   wait for shot goal to be created (with optional shot-choice from user)
    #   create shot goal on guide side (possibly with shot-choice from user or possibly put guide-generated shot choice)
    #     and put completed=false, performance information (from last time they worked on this shot)

    #   loop until shot goal == completed

    #       wait for stat/baseline goal to be created
    #       if baseline goal, create baseline goal and put completed=false
    #           wait for completed == true, end baseline goal and use that to generate shot choice
    #           wait for stat goal to be created
    #           create stat goal on guide side and put completed=false, stat choice, plus performance, target and score
    #             information (from last time they worked on this stat)
    #       else if stat goal,
    #           create stat goal on guide side and put completed=false, performance, target and score information (from
    #             last time they worked on this stat) (user's stat-choice)

    #       loop until stat goal == completed

    #           wait for set goal to be created
    #           create goal on guide side and put completed=false

    #           loop until set goal == completed

    #               wait for action goal to be created
    #               continually post shot scores after each shot the user plays, deleting all previously posted scores
    #                 each shot

    #           end set goal on guide side and put performance, target and avg_score info for set just completed

    #       end stat goal on guide side and put performance, target and avg_score info for stat just completed

    #   end shot goal on guide side and put performance, target and avg_score info for shot just completed

    # end session goal on guide side and put performance, target and avg_score info for session just completed
