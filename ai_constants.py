import ai_engine
import custom_ai_engines

# available agents
# custom_ai_engines.random_agent()
# custom_ai_engines.minimax_alpha_beta_agent(depth=3)

# white ai
AI1 = custom_ai_engines.q_agent(explore_rate = 0.2,file="agent1.2")
# black ai
AI2 = custom_ai_engines.q_agent(explore_rate = 0.2,file="agent2.2")
#AI2 = custom_ai_engines.minimax_alpha_beta_agent(depth=2, heuristic=custom_ai_engines.piece_value_heuristic())