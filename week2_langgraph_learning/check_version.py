import langchain
import langgraph
import pkg_resources

print("langchain version:", langchain.__version__)
print("langgraph version:", pkg_resources.get_distribution("langgraph").version)

# langchain version: 0.3.26
# langgraph version: 0.5.1