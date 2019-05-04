from graphqlclient import GraphQLClient

client = GraphQLClient('https://hackerone.com/directory')

print dir(client)
