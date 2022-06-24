from typing import List, Tuple
import clr
import sys
clr.AddReference('Microsoft.AnalysisServices.AdomdClient')
clr.AddReference('Microsoft.AnalysisServices.Tabular')
clr.AddReference('Microsoft.AnalysisServices')
from InquirerPy.base.control import Choice
from InquirerPy import inquirer, get_style
from Microsoft.AnalysisServices.AdomdClient import AdomdCommand, AdomdConnection
from Microsoft.AnalysisServices.Tabular import Server, Database, RefreshType
from Microsoft.AnalysisServices import UpdateOptions

style = get_style({"questionmark":"blue","answermark":"blue"})



CONNECTION_STR = {"FIN 300": "Data Source=asazure://centralus.asazure.windows.net/azraasdaientdlfn300:rw;Initial Catalog=FINANCE;Cube=Model;User ID=svc-azssas-process-p@rockwellautomation.com;Password=');!3xk3YlB(Fatf'",
                  "FIN 500": "Data Source=asazure://centralus.asazure.windows.net/azraasdaientdlfn500:rw;Initial Catalog=FINANCE;Cube=Model;User ID=svc-azssas-process-p@rockwellautomation.com;Password=');!3xk3YlB(Fatf'",
                  "FIN 700": "Data Source=asazure://centralus.asazure.windows.net/azraasdaientdlfn700:rw;Initial Catalog=FINANCE;Cube=Model;User ID=svc-azssas-process-p@rockwellautomation.com;Password=');!3xk3YlB(Fatf'"}

def iterator(collection) -> List[Tuple]:
	'''
	Input a collection from Microsoft.Analysis.Services.Tabular.
	It will iterate through the C# collection and return a List[Tuple]
	Ex. [(Index,Collection Item, Name of Item)]
	'''
	return [(index, collection.get_Item(index).Name,collection.get_Item(index)) for index in range(len(collection))]






class Connection:
	def __init__(self,CONNECTION_STR=CONNECTION_STR['FIN 500'],Database_Index=0):
		self.Server = Server()
		self.Server.Connect(CONNECTION_STR)
		self.Database = self.Server.Databases[Database_Index]
		self.Model = self.Database.Model
		pass
	def pick_db(self,db_name='FINANCE'):
		databases = [(x, self.Server.Databases[x].get_Name()) for x in range(0, len(self.Server.Databases))]
		#db = self.Server.Databases[database_index]
		return databases

class Refresh(Connection):
	def __init__(self,Collections,RefreshType = RefreshType.Full, UpdateOptions = UpdateOptions.ExpandFull):
		self.Collections = Collections
		pass
	def Run(self):
		for collection in self.Collections:
			collection.RequestRefresh(RefreshType.Full)
		return self.Database.Update(UpdateOptions)

def cli():
	server_str = inquirer.select(
		message = "What do you want to access?:",
		choices = [server for server in CONNECTION_STR.keys()],
		style=style,
		default = None).execute()
	server = Server()
	server.Connect(CONNECTION_STR[server_str])

	databases = [server.Databases[x].get_Name() for x in range(0, len(server.Databases))]
	database_index = inquirer.select(
		message="Which DB do you want to access?",
		choices=[Choice(key, name=db_name) for key, db_name in enumerate(databases)],
		style=style
		).execute()
	database = server.Databases[database_index]
	command = inquirer.select(
		message = f"What do you want to do? You are currently connected to {databases[database_index]} in {server_str}",
		choices = ["Refresh Table","Refresh Partitions","Check Memory"],
		style= style
	).execute()
	tables = [(table_index,database.Model.Tables.get_Item(table_index).get_Name()) for table_index in range(0,database.Model.Tables.Count)]
	select_tables = inquirer.text(
		message =f"What table do you want to refresh?",
		completer = {database.Model.Tables.get_Item(table_index).get_Name():None for table_index in range(0,database.Model.Tables.Count)},
		style=style
	)
	match command:
		case "Refresh Table":
			table_to_refresh = select_tables.execute()
			table_index_to_refresh = [item[0] for item in tables if item[1] == table_to_refresh]

			for index in table_index_to_refresh:
				database.Model.Tables.get_Item(index).RequestRefresh(RefreshType.Full)

			confirm_refresh = inquirer.confirm(
				message=f"Execute Refresh Now?"
			).execute()
			if confirm_refresh:
				database.Update(UpdateOptions.ExpandFull)
			return True
		case "Refresh Partitions":
			select_tables._message = "From what table do you want to refresh partitions?"
			table = select_tables.execute()
			table_index_to_refresh = [item[0] for item in tables if item[1] == table]


		case "Check Memory":
			print(database.get_EstimatedSize())
	return database




if __name__ == '__main__':
	cli()








'''
conn = AdomdConnection()
conn.ConnectionString = CONNECTION_STR["FIN 300"]
conn.Open()
query = AdomdCommand('EVALUATE TOPN(1000,FACT_COPA)', conn).ExecuteReader()
while query.Read()
Read() will start at the first row and keep returning true if it finds data
'''