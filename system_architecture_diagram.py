# system_architecture_final.py
from diagrams import Diagram, Edge, Cluster
from diagrams.programming.language import Python
from diagrams.onprem.database import Mysql
from diagrams.onprem.client import User
from diagrams.aws.integration import SQS
from diagrams.generic.compute import Rack
from diagrams.generic.database import SQL
from diagrams.onprem.container import Docker
from diagrams.onprem.inmemory import Redis

# Use SQS as generic API gateway
APIGateway = SQS

with Diagram(
    "A Machine Learning Based Tourism Recommendation Web App - System Architecture",
    show=False,
    direction="TB",
    filename="system_architecture",
    outformat="png",
    graph_attr={
        "fontsize": "20",           # Larger main title font
        "fontname": "Arial Bold",
        "labeljust": "c",
        "nodesep": "0.8",
        "ranksep": "0.8"
    }
):
    # ========== PRESENTATION LAYER (TOP TIER) ==========
    with Cluster("Presentation Layer - Streamlit Frontend", graph_attr={
        "fontsize": "18",
        "fontname": "Arial Bold"
    }):
        user = User("End User")
        
        with Cluster("UI Components", graph_attr={
            "fontsize": "16",
            "fontname": "Arial"
        }):
            navbar = Rack("Navbar")
            homepage = Rack("Homepage Dashboard")
            ai_chat = Rack("AI Assistant Chat")
            destination_page = Rack("Destination Details")
            wishlist_page = Rack("Wishlist")
            expense_page = Rack("Expense Tracker")
    
    # ========== APPLICATION LOGIC LAYER (MIDDLE TIER) ==========
    with Cluster("Application Logic Layer - Python Backend", graph_attr={
        "fontsize": "18",
        "fontname": "Arial Bold"
    }):
        auth = Python("Authentication")
        ai_engine = Python("AI Assistant\n(Llama 3.2)")
        db_handler = Python("Database Handler")
        api_handler = Python("API Integration")
        
        # AI processing sub-cluster
        with Cluster("AI Processing", graph_attr={
            "fontsize": "16",
            "fontname": "Arial"
        }):
            llama = Docker("Ollama\n(Llama 3.2 3B)")
    
    # ========== DATA LAYER (BOTTOM TIER) ==========
    with Cluster("Data Layer - MySQL Database", graph_attr={
        "fontsize": "18",
        "fontname": "Arial Bold"
    }):
        mysql_db = Mysql("MySQL Database\n(12 Tables)")
    
    # ========== EXTERNAL SERVICES ==========
    with Cluster("External APIs", graph_attr={
        "fontsize": "18",
        "fontname": "Arial Bold"
    }):
        unsplash = APIGateway("Unsplash API")
        weather = APIGateway("OpenWeatherMap")
        # Currency API removed
    
    # ========== CONNECTIONS ==========
    # User to UI
    user >> Edge(color="blue", penwidth="2.5") >> navbar
    navbar >> Edge(color="blue", penwidth="2") >> homepage
    navbar >> Edge(color="blue", penwidth="2") >> ai_chat
    navbar >> Edge(color="blue", penwidth="2") >> destination_page
    navbar >> Edge(color="blue", penwidth="2") >> wishlist_page
    navbar >> Edge(color="blue", penwidth="2") >> expense_page
    
    # UI to Application Layer
    homepage >> Edge(label="Auth Request", fontsize="12", penwidth="2") >> auth
    ai_chat >> Edge(label="Generate Plan", fontsize="12", penwidth="2") >> ai_engine
    destination_page >> Edge(label="Fetch Data", fontsize="12", penwidth="2") >> api_handler
    wishlist_page >> Edge(label="Save/Delete", fontsize="12", penwidth="2") >> db_handler
    expense_page >> Edge(label="Track", fontsize="12", penwidth="2") >> db_handler
    
    # AI Engine to Llama
    ai_engine >> Edge(label="Prompt", fontsize="12", penwidth="2") >> llama
    llama >> Edge(label="Response", fontsize="12", penwidth="2") >> ai_engine
    
    # Application to Database
    auth >> Edge(label="CRUD", fontsize="12", penwidth="2") >> mysql_db
    db_handler >> Edge(label="SQL Queries", fontsize="12", penwidth="2") >> mysql_db
    api_handler >> Edge(label="Store/Fetch", fontsize="12", penwidth="2") >> mysql_db
    
    # Application to External APIs
    api_handler >> Edge(label="Images", fontsize="12", penwidth="2") >> unsplash
    api_handler >> Edge(label="Weather", fontsize="12", penwidth="2") >> weather
    # Currency connection removed

print("✅ System Architecture Diagram generated as 'system_architecture.png'")