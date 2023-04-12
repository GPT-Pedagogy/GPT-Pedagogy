import connection
import pandas as pd



'''Generate the student's performances to the teacher. '''
def generate_performance():
    db = connection.connection()
  
    # Retrieve all documents from the performance_data collection
    performance_docs = db.find({})

    # Create an empty dictionary to store the performance data for each student
    all_performance_data = {}


    # Iterate over each document in the collection
    for doc in performance_docs:
        rcsid = doc["RCSid"]
        performance_data = doc["Performance"]

        # Add the performance data for the current student to the dictionary
        all_performance_data[rcsid] = performance_data
    
    # Create a list to store the data for each row in the output sheet
    data = []

    # Keep track of the previous student's RCS ID and topic
    prev_rcsid = ""
    prev_topic = ""

    # Iterate over the performance data for each student and store it in the data list
    for rcsid, performance in all_performance_data.items():
        topic_dict = {}
        for chapter, chapter_data in performance.items():
            topic = chapter_data["Topic"]
            if topic not in topic_dict:
                topic_dict[topic] = []
            questions = chapter_data["Outcome"]
            for question_number, result in questions.items():
                topic_dict[topic].append([rcsid, chapter, topic, question_number, result])

    # Add blank rows between different students
        if prev_rcsid and prev_rcsid != rcsid:
            data.extend([["", "", "", "", ""], ["", "", "", "", ""]])

        # Iterate over the topics for the current student
        for topic, questions in topic_dict.items():

            # Add blank row between different topics
            if prev_topic and prev_topic != topic:
                data.append(["", "", "", "", ""])

            # Add RCS ID, Chapter, and Topic fields for the first question for the topic
            if len(questions) == 1:
                question = questions[0]
                data.append([question[0], question[1], question[2], question[3], question[4]])

            # Add RCS ID, Chapter, and Topic fields for the first question and leave them blank for others
            else:
                for i, question in enumerate(questions):
                    if i == 0:
                        data.append([question[0], question[1], question[2], question[3], question[4]])
                    else:
                        data.append(["", "", "", question[3], question[4]])

            # Set previous topic
            prev_topic = topic

        # Set previous RCS ID
        prev_rcsid = rcsid

    # Create a pandas DataFrame from the data list
    df = pd.DataFrame(data, columns=["RCS ID", "Chapter", "Topic", "Question Number", "Result"])

    # Export the DataFrame to an Excel sheet
    with pd.ExcelWriter('students_performance.xlsx', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        writer._save()

        
generate_performance()