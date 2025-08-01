from core.agent.cv_reader_agent import CV_Reader_Agent

agent_reader = CV_Reader_Agent()
candidate_information = agent_reader.get_information_from_CV(r'CV_data\INFORMATION-TECHNOLOGY\10265057.pdf')
print(candidate_information)