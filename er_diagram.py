# simple_erd.py
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(1, 1, figsize=(14, 18))
ax.set_xlim(0, 14)
ax.set_ylim(0, 18)
ax.axis('off')


# Colors
colors = {
    'core': '#3498DB',    # Blue
    'user': '#2ECC71',    # Green
    'group': '#E67E22'    # Orange
}

# ============================================================
# TABLE 1: USERS (Top Center)
# ============================================================
users = FancyBboxPatch((4, 14), 6, 3, boxstyle="round,pad=0.1", 
                       facecolor=colors['core'], edgecolor='#2C3E50', linewidth=2)
ax.add_patch(users)
ax.text(7, 16.5, "USERS", fontsize=12, fontweight='bold', color='white', ha='center')
ax.text(4.3, 15.8, "🔑 id (PRIMARY KEY)", fontsize=9, color='white')
ax.text(4.3, 15.1, "📧 username", fontsize=9, color='white')
ax.text(4.3, 14.4, "📧 email", fontsize=9, color='white')

# ============================================================
# TABLE 2: DESTINATIONS (Below Users)
# ============================================================
dest = FancyBboxPatch((4, 10), 6, 3, boxstyle="round,pad=0.1", 
                      facecolor=colors['core'], edgecolor='#2C3E50', linewidth=2)
ax.add_patch(dest)
ax.text(7, 12.5, "DESTINATIONS", fontsize=12, fontweight='bold', color='white', ha='center')
ax.text(4.3, 11.8, "🔑 id (PRIMARY KEY)", fontsize=9, color='white')
ax.text(4.3, 11.1, "🌍 country", fontsize=9, color='white')
ax.text(4.3, 10.4, "🏙️ city", fontsize=9, color='white')

# ============================================================
# TABLE 3: WISHLIST (Left)
# ============================================================
wish = FancyBboxPatch((0.5, 5), 5.5, 3.5, boxstyle="round,pad=0.1", 
                      facecolor=colors['user'], edgecolor='#2C3E50', linewidth=2)
ax.add_patch(wish)
ax.text(3.25, 8, "WISHLIST", fontsize=11, fontweight='bold', color='white', ha='center')
ax.text(0.8, 7.2, "🔑 id (PRIMARY KEY)", fontsize=9, color='white')
ax.text(0.8, 6.5, "🔗 user_id (FOREIGN KEY)", fontsize=8, color='white')
ax.text(0.8, 5.8, "🔗 destination_id (FOREIGN KEY)", fontsize=8, color='white')
ax.text(0.8, 5.1, "📝 personal_notes", fontsize=8, color='white')

# ============================================================
# TABLE 4: REVIEWS (Center)
# ============================================================
review = FancyBboxPatch((7.5, 5), 5.5, 3.5, boxstyle="round,pad=0.1", 
                        facecolor=colors['user'], edgecolor='#2C3E50', linewidth=2)
ax.add_patch(review)
ax.text(10.25, 8, "REVIEWS", fontsize=11, fontweight='bold', color='white', ha='center')
ax.text(7.8, 7.2, "🔑 id (PRIMARY KEY)", fontsize=9, color='white')
ax.text(7.8, 6.5, "🔗 user_id (FOREIGN KEY)", fontsize=8, color='white')
ax.text(7.8, 5.8, "🔗 destination_id (FOREIGN KEY)", fontsize=8, color='white')
ax.text(7.8, 5.1, "⭐ rating (1-5)", fontsize=8, color='white')

# ============================================================
# TABLE 5: EXPENSE TRACKER (Bottom Left)
# ============================================================
expense = FancyBboxPatch((0.5, 0.5), 5.5, 3.5, boxstyle="round,pad=0.1", 
                         facecolor=colors['group'], edgecolor='#2C3E50', linewidth=2)
ax.add_patch(expense)
ax.text(3.25, 3.5, "EXPENSE TRACKER", fontsize=10, fontweight='bold', color='white', ha='center')
ax.text(0.8, 2.7, "🔑 id (PRIMARY KEY)", fontsize=9, color='white')
ax.text(0.8, 2.0, "🔗 user_id (FOREIGN KEY)", fontsize=8, color='white')
ax.text(0.8, 1.3, "💰 amount", fontsize=8, color='white')
ax.text(0.8, 0.6, "📂 category", fontsize=8, color='white')

# ============================================================

# ============================================================
# RELATIONSHIP ARROWS
# ============================================================

# USERS → WISHLIST
ax.annotate("", xy=(3.25, 8.5), xytext=(5.5, 14), 
            arrowprops=dict(arrowstyle="->", lw=2, color='red'))
ax.text(4, 11, "1 : M", fontsize=9, color='red', fontweight='bold', ha='center')

# USERS → REVIEWS
ax.annotate("", xy=(10.25, 8.5), xytext=(8.5, 14), 
            arrowprops=dict(arrowstyle="->", lw=2, color='red'))
ax.text(9.3, 11, "1 : M", fontsize=9, color='red', fontweight='bold', ha='center')

# USERS → EXPENSE TRACKER
ax.annotate("", xy=(3.25, 4), xytext=(5.5, 14), 
            arrowprops=dict(arrowstyle="->", lw=2, color='red', connectionstyle="arc3,rad=-0.2"))
ax.text(4.2, 9, "1 : M", fontsize=9, color='red', fontweight='bold', ha='center')



# DESTINATIONS → WISHLIST
ax.annotate("", xy=(3.25, 8.5), xytext=(5.5, 10), 
            arrowprops=dict(arrowstyle="->", lw=2, color='purple'))
ax.text(4.5, 9.2, "1 : M", fontsize=9, color='purple', fontweight='bold', ha='center')

# DESTINATIONS → REVIEWS
ax.annotate("", xy=(10.25, 8.5), xytext=(8.5, 10), 
            arrowprops=dict(arrowstyle="->", lw=2, color='purple'))
ax.text(9.5, 9.2, "1 : M", fontsize=9, color='purple', fontweight='bold', ha='center')



ax.text(0.5, 17.3, "🔑 PK = Primary Key | 🔗 FK = Foreign Key", fontsize=8, color='#333')
ax.text(0.5, 16.7, "1:M = One to Many Relationship", fontsize=8, color='#333')

plt.tight_layout()
plt.savefig('erd.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.show()
print("✅ ER Diagram saved as 'erd.png'")