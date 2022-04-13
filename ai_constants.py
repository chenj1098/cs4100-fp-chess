import ai_engine
import custom_ai_engines

# available agents
# custom_ai_engines.random_agent()
# custom_ai_engines.minimax_alpha_beta_agent(depth=3)

# white ai
AI1 = custom_ai_engines.minimax_alpha_beta_agent(depth=3)
# black ai
AI2 = custom_ai_engines.minimax_alpha_beta_agent(depth=3)