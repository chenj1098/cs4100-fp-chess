import ai_engine
import custom_ai_engines

# available agents
# custom_ai_engines.random_agent()
# custom_ai_engines.minimax_alpha_beta_agent(depth=3)

# white ai
#AI1 = custom_ai_engines.q_agent(explore_rate = 0.2,learn_rate = 0.5,file="agent1.2")
AI1 = custom_ai_engines.minimax_alpha_beta_agent(depth=3, heuristic=custom_ai_engines.piece_squares_table_heuristic())
#AI1 = custom_ai_engines.random_agent()
# black ai
#AI2 = custom_ai_engines.q_agent(explore_rate = 0.5,learn_rate = 0.5,file="agent2.2")
AI2 = custom_ai_engines.minimax_alpha_beta_agent(depth=3, heuristic=custom_ai_engines.piece_value_heuristic())
#AI2 = custom_ai_engines.suicide_minimax_alpha_beta_agent(depth=3, heuristic=custom_ai_engines.suicide_heuristic())