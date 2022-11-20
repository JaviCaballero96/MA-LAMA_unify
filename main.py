import os
import fnmatch


if __name__ == '__main__':

    dir_path = '/home/javier/Desktop/planners/outPreprocess/'
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
        for line in file:
            if "Cost:" not in line:
                duration = line.split("(")[0].strip()
                line = line.split("(")[1:][0]
                name = line.split(")")[0]
                cost = line.split(")")[1].strip()
                read_plan.append([duration, name, cost, float(time)])
                if "_start" in name:
                    time = time + float(duration)
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

        # get the candidate with the minimum start time
        action_to_include = None
        for action in candidates:
            if action is not None:
                if action_to_include is None:
                    action_to_include = action
                else:
                    if action_to_include[2][3] > action[2][3]:
                        action_to_include = action

        # include an action
        if action_to_include is not None:
            final_plan.append(action_to_include)
            agent_counter[action_to_include[1]] = action_to_include[0] + 1
            agent_tick[action_to_include[1]] = action_to_include[2][3]

            if agent_counter[action_to_include[1]] >= len(read_plans[action_to_include[1]]):
                agent_plan_finished[action_to_include[1]] = True
                all_plans_finished = True
                for boolean_finished in agent_plan_finished:
                    if not boolean_finished:
                        all_plans_finished = False
                        break
        else:
            tick = tick + 0.01

        iterations = iterations + 1

    # print only start actions in final plan
    plan_cost = 0
    final_plan_file = open(dir_path + "final_plan.txt", 'w')
    for action in final_plan:
        if "_start" in action[2][1]:
            action_name = action[2][1].split("_start")[0] + action[2][1].split("_start")[1]
            action_init = action[2][3]
            plan_cost = plan_cost + float(action[2][2])
            final_plan_file.write("{:.3f}".format(action_init) + " " + str(action_name) + "\n")
        else:
            plan_cost = plan_cost + float(action[2][2])

    final_plan_file.write("Cost: " + str(plan_cost) + "\n")
    final_plan_file.close()
    print("end")





