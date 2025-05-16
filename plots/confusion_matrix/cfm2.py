import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

# Define confusion matrices for each hierarchy level

# HL1
hl1_labels = ["MosfetDiode", "load_cap", "compensation_cap"]
hl1_matrix = np.array([[1952, 0, 0], [0, 215, 0], [0, 0, 405]])

# HL2
hl2_labels = ["CM", "Inverter", "DiffPair"]
hl2_matrix = np.array(
    [[4241, 451, 14], [1120, 687, 51], [10, 20, 260]]  # CM  # Inverter  # DiffPair
)

# HL3
hl3_labels = [
    "firstStage",
    "secondStage",
    "thirdStage",
    "loadPart",
    "biasPart",
    "feedBack",
]
hl3_matrix = np.array(
    [
        [600, 0, 0, 0, 0, 20],  # firstStage
        [0, 109, 0, 0, 659, 0],  # secondStage
        [0, 55, 0, 0, 100, 0],  # thirdStage
        [0, 35, 0, 763, 592, 0],  # loadPart
        [0, 181, 0, 0, 3749, 0],  # biasPart
        [0, 0, 0, 0, 340, 0],  # feedBack
    ]
)

# Plotting
fig, axs = plt.subplots(
    1,
    3,
    figsize=(15, 8.5),
)
sns.set(style="whitegrid")
sns.set(font_scale=1.4)
# HL1 Plot
sns.heatmap(
    hl1_matrix,
    annot=True,
    fmt="d",
    xticklabels=hl1_labels,
    yticklabels=hl1_labels,
    ax=axs[0],
    cmap="Blues",
    cbar=False,
    square=True,
)
axs[0].set_title("Hierarchical Level 1", fontsize=20)
# axs[0].set_xlabel("Predicted")
axs[0].set_ylabel("Actual", fontsize=15)
axs[0].set_xticklabels(
    axs[0].get_xticklabels(),
    rotation=30,
    fontsize=15,
    ha="right",
    rotation_mode="anchor",
)
axs[0].set_yticklabels(
    axs[0].get_yticklabels(),
    fontsize=10,
    rotation=90,
)


# HL2 Plot
sns.heatmap(
    hl2_matrix,
    annot=True,
    fmt="d",
    xticklabels=hl2_labels,
    yticklabels=hl2_labels,
    ax=axs[1],
    cmap="Greens",
    cbar=False,
    square=True,
)
axs[1].set_title("Hierarchical Level 2", fontsize=20)
axs[1].set_xlabel("Predicted", fontsize=15)
# axs[1].set_ylabel("Actual")
axs[1].set_xticklabels(axs[1].get_xticklabels(), fontsize=15)
axs[1].set_yticklabels(axs[1].get_yticklabels(), fontsize=15)
# HL3 Plot
sns.heatmap(
    hl3_matrix,
    annot=True,
    fmt="d",
    xticklabels=hl3_labels,
    yticklabels=hl3_labels,
    ax=axs[2],
    cmap="Oranges",
    cbar=False,
    square=True,
    annot_kws={"fontsize": 12},
)
axs[2].set_title("Hierarchical Level 3", fontsize=20)
# axs[2].set_xlabel("Predicted")
# axs[2].set_ylabel("Actual")
axs[2].set_xticklabels(
    axs[2].get_xticklabels(),
    rotation=30,
    fontsize=15,
    ha="right",
    rotation_mode="anchor",
)
axs[2].set_yticklabels(axs[2].get_yticklabels(), fontsize=15)

# axs[2].set_yticklabels(axs[2].get_yticklabels(), rotation=30)


plt.tight_layout()
# plt.subplots_adjust(left=0.03, right=0.8, top=0.9, bottom=0.22, wspace=0.37, hspace=0.4)

plt.savefig("v2.png", dpi=300)
plt.savefig("cfm-v2.pdf", dpi=300)
plt.show()
