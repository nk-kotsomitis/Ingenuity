import numpy as np
import matplotlib.pyplot as plt


# total_size | IRAM | .text | .vectors |  DIRAM | .bss |  .data | .text | Flash Code | .text | Flash Data | .rodata | .appdesc | RTC FAST | .rtc_reserved
# 0: "total", 1: "IRAM_total", 2: ".text" (child_of_IRAM_total,

keys = [
            "Total size", "IRAM", "  .text", "  .vectors", "DIRAM", "  .bss", "  .data",
            "  .text", "Flash Code", "  .text", "Flash Data", "  .rodata", "  .appdesc",
            "RTC FAST", "  .rtc_reserved"
        ]

values = [283370, 20, 20, 0, 283350, 1282, 281502, 566, 0, 0, 0, 0, 0, 0, 0]

sizes_component = list(zip(keys, values))
sizes_component = sizes_component[1:] + [sizes_component[0]]

print(sizes_component)

if False:
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.axis("off")
    table = ax.table(cellText=sizes_component, colLabels=["Memory Section", "Size [Bytes]"], loc="center", cellLoc="left", edges='vertical')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width([0, 1])
    table.scale(1, 1.2)

    for (i, j), cell in table.get_celld().items():
        if i == 0:  # Header row
            cell.set_text_props(weight='bold', )  # backgroundcolor='#0d0d0d'
            cell.set_facecolor("#000000")  # Light gray background
    plt.show()

if False:
    import numpy as np
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D


    error_categories = np.array([-2, -1, 0,  1, 2])


    inference_ids_1 = np.array([4, 4, 4, 4, 4])
    inference_ids_2 = np.array([3, 3, 3, 3, 3])
    inference_ids_3 = np.array([2, 2, 2, 2, 2])
    inference_ids_4 = np.array([1, 1, 1, 1, 1])


    hist_1 = np.array([40, 500, 1000, 200, 40])
    hist_2 = np.array([30, 700, 900, 100, 50])
    hist_3 = np.array([30, 700, 900, 100, 50])
    hist_4 = np.array([30, 700, 900, 100, 50])

    # Create 3D figure
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection='3d')
    # Bar width
    dx = 0.9
    dy = 0.2

    ax.bar3d(error_categories, inference_ids_1, np.zeros_like(hist_1), dx, dy, hist_1, color='#5b95c2', alpha=1.0, label="Current")
    ax.bar3d(error_categories, inference_ids_2, np.zeros_like(hist_2), dx, dy, hist_2, color='#5b95c2', alpha=0.5, label="Previous")
    ax.bar3d(error_categories, inference_ids_3, np.zeros_like(hist_3), dx, dy, hist_3, color='#5b95c2', alpha=0.2, label="Previous")
    ax.bar3d(error_categories, inference_ids_4, np.zeros_like(hist_4), dx, dy, hist_4, color='#5b95c2', alpha=0.1, label="Previous")


    # ax.xaxis.label.set_color('red')   # X-axis label color
    # ax.yaxis.label.set_color('green') # Y-axis label color
    # ax.zaxis.label.set_color('blue')  # Z-axis label color

    # ax.tick_params(axis='x', colors='red')
    # ax.tick_params(axis='y', colors='green')
    # ax.tick_params(axis='z', colors='blue')

    ax.xaxis._axinfo['grid'].update(color='white', linestyle='solid')
    ax.yaxis._axinfo['grid'].update(color='white', linestyle='solid')
    ax.zaxis._axinfo['grid'].update(color='white', linestyle='solid')

    ax.xaxis.set_pane_color('white')  # Or any color you prefer
    ax.yaxis.set_pane_color('white')  # Or any color you prefer
    ax.zaxis.set_pane_color('white')  # Or any color you prefer

    # Labels and Titles
    ax.set_xlabel("Error Category")
    ax.set_ylabel("Inference Counter")
    ax.set_zlabel("Frequency")
    # ax.set_title("3D Histogram: Current vs. Previous Errors")
    ax.set_xticks([-2, -1, 0, 1, 2])
    ax.set_yticks([1, 2, 3, 4])
    ax.set_ylim(4, 1)
    # ax.legend(loc='upper left')

    ax.view_init(elev=30, azim=45)
    ax.set_proj_type('ortho')
    plt.ioff()
    plt.show()


a = {'DIRAM': ['333188', '97.49', '8572', '341760'], '.bss': ['292036', '85.45'], '.data': ['37539', '10.98'], '.text': ['15356', '93.73'], 'Flash Code': ['89320', '1.06', '8299256', '8388576'], 'Flash Data': ['42464', '0.13', '33511936', '33554400'], '.rodata': ['42208', '0.13'], '.appdesc': ['256', '0.0'], 'IRAM': ['16383', '99.99', '1', '16384'], '.vectors': ['1027', '6.27'], 'RTC FAST': ['280', '3.42', '7912', '8192'], '.rtc_reserved': ['24', '0.29']}
