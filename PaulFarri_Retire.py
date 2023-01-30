"""This simple Python Program collects user input
and computes retirement planning advice
Written by: 
Paul Farri
for LU's CSIS 110 course 
D02
Be sure you fully document your code with 
comments like you see here."""



"""
Starting statements collects the necessary information from the user via input Statements
"""

Full_Name = input ('Please enter your full name: ')
Current_Age = int(input ('Please enter your current age: '))
Desired_Retire_Age = int(input ('Please enter the desired retirement age: '))
Current_Retire_Savings = float(input ('Please enter your current retirement savings: '))
Amount_Needed = float(input ('Please enter the amount needed: '))


""" Prints results collected from user inputs """
print([Full_Name, Current_Age, Desired_Retire_Age, Current_Retire_Savings, Amount_Needed])


""" Utilizes if statements with greater than/less than conditions, printing result based on user responses """
if Current_Age < Desired_Retire_Age and Current_Retire_Savings < Amount_Needed: 
    print("This person", Full_Name, "has", Desired_Retire_Age - Current_Age, "years before they are ready to retire.") 
    print ("This person", Full_Name, "has not yet reached their retirement savings goal. They require", Amount_Needed - Current_Retire_Savings, "before they reach their goal.")


if Current_Age > Desired_Retire_Age and Current_Retire_Savings > Amount_Needed:
    print("This person", Full_Name,"" "has reached the age of retirement at", Current_Age, "and has met their retirement savings goal at", Current_Retire_Savings, "!")