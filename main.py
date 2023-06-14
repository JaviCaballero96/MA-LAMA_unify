import os
import fnmatch


def takeTime(elem):
    return elem[2][3]


def reinitialiseInternalCLock(plan, agent_counter, tick):

    if agent_counter < (len(plan) - 1):
        extra_time = tick - plan[agent_counter][3]

        if extra_time != 0:
            for acti in plan[agent_counter + 1:]:
                acti[3] = acti[3] + extra_time


if __name__ == '__main__':

    dir_path = os.getcwd() + "/"
    count = -1
    agent_number = 0
    filename_per_agent = []
    file_per_agent = []

    # Count agents number and get the last solution found for each
    while count != 0:
        match = 'output_preproagent' + str(agent_number) + '.*'
        count = len(fnmatch.filter(os.listdir(dir_path), match))
        if count != 0:
            files_per_agent = fnmatch.filter(os.listdir(dir_path), match)
            files_per_agent.sort(reverse=True)
            filename_per_agent.append(files_per_agent[0])
            file_per_agent.append(open(dir_path + filename_per_agent[agent_number], "r"))
            print("Agent " + str(agent_number) + " --> " + filename_per_agent[agent_number])
        agent_number = agent_number + 1
        # print(match + " -> Agent " + str(agent_number) + ": " + str(count))

    agent_number = agent_number - 1
    print(str(agent_number) + " agents detected")

    # read all agent plans
    read_plans = []
    for file in file_per_agent:
        read_plan = []
        time = 0
        line_number = 0
        append_bool = True
        for line in file:
            if "Cost:" not in line:
                duration = line.split("(")[0].strip()

                # extract constraints
                constraints_list_num = []
                if "no_constraints" in line:
                    constraints_list = []
                    line = line.split("no_constraints")[0]
                else:
                    constraints = (line.split("(")[2:][0]).split(")")[0]
                    constraints_list_aux = constraints.split("|")
                    constraints_list = [con.split(" ") for con in constraints_list_aux]
                    for con_list in constraints_list:
                        constraints_list_num.append([int(con) for con in con_list])

                line = line.split("(")[1:][0]
                name = line.split(")")[0]
                cost = line.split(")")[1].strip()
                read_plan.append([duration, name, cost, float(time), constraints_list_num])
                if "_start" in name:
                    time = time + float(duration)

            else:
                if line_number == 0:
                    append_bool = False
                    agent_number = agent_number - 1
                    break

            line_number = line_number + 1

        if append_bool:
            read_plans.append(read_plan)

    for a_file in file_per_agent:
        a_file.close()

    # Create final plan
    final_plan = []
    all_plans_finished = False
    agent_plan_finished = [False] * agent_number
    agent_counter = [0] * agent_number
    tick = 0
    agent_tick = [0] * agent_number

    # we will only finish this when all plans have finished
    iterations = 0
    current_constraints = {}
    while not all_plans_finished:
        agent_checked = 0
        candidates = [None] * agent_number

        # get counter actions that have a start time minor than the general tick
        for agent_plan in read_plans:
            # Check if counter action can be added
            if not agent_plan_finished[agent_checked]:
                action = agent_plan[agent_counter[agent_checked]]

                # an action can be added if the tick time is greater and there are no other agent actions with less tick
                if tick >= action[3]:
                    candidates[agent_checked] = [agent_counter[agent_checked], agent_checked, action]

            agent_checked = agent_checked + 1

        added_action = False
        while not added_action:

            all_none = True
            for act in candidates:
                if act is not None:
                    all_none = False
            if all_none:
                tick = tick + 0.001
                break

            # get the candidate with the minimum start time
            action_to_include = None
            for action in candidates:
                if action is not None:
                    if action_to_include is None:
                        action_to_include = action
                    else:
                        if action_to_include[2][3] > action[2][3]:
                            action_to_include = action

            if action_to_include is not None:
                valid_candidate = True

                # check if the chosen candidate can be added by its constraints
                if action_to_include[2][4]:
                    for can_const in action_to_include[2][4]:
                        if valid_candidate:
                            if can_const[2] == -1:
                                continue
                            for cur_const, cur_const_value in current_constraints.items():
                                # if the affected var is the same and the value is not, candidate has to wait
                                if valid_candidate and can_const[1] == cur_const and can_const[2] != cur_const_value:
                                    valid_candidate = False

                if valid_candidate:
                    added_action = True
                    # apply candidate constraints to current
                    for can_const in action_to_include[2][4]:
                        if can_const[0] == 1:
                            current_constraints[can_const[1]] = can_const[3]
                    # include an action
                    reinitialiseInternalCLock(read_plans[action_to_include[1]], agent_counter[action_to_include[1]]
                                              , tick)
                    final_plan.append(action_to_include)
                    agent_counter[action_to_include[1]] = action_to_include[0] + 1
                    # agent_tick[action_to_include[1]] = action_to_include[2][3]
                    agent_tick[action_to_include[1]] = tick
                    action_to_include[2][3] = agent_tick[action_to_include[1]]

                    if agent_counter[action_to_include[1]] >= len(read_plans[action_to_include[1]]):
                        agent_plan_finished[action_to_include[1]] = True
                        all_plans_finished = True
                        for boolean_finished in agent_plan_finished:
                            if not boolean_finished:
                                all_plans_finished = False
                                break
                else:
                    candidates.remove(action_to_include)

            else:
                tick = tick + 0.001

        iterations = iterations + 1

    # print only start actions in final plan
    plan_cost = 0
    final_plan_file = open(dir_path + "final_plan.txt", 'w')
    final_plan.sort(key=takeTime)
    for action in final_plan:
        if "_start" in action[2][1]:
            action_name = action[2][1].split("_start")[0] + action[2][1].split("_start")[1]
            action_init = action[2][3]
            action_duration = float(action[2][0])
            plan_cost = plan_cost + float(action[2][2])
            final_plan_file.write("{:.3f}".format(action_init) + " " + "({:.3f})".format(action_duration) + " " + str(action_name) + "\n")
        else:
            plan_cost = plan_cost + float(action[2][2])

    final_plan_file.write("Cost: " + str(plan_cost) + "\n")
    final_plan_file.close()
    print("end")
