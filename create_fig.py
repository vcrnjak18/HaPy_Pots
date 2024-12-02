import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def create_figure(sun, hum, salt, fert):
    fig, ax = plt.subplots(figsize = (6,4))
    fig.patch.set_facecolor('#ffffff')

    height = [sun, hum, salt, fert]

    tick_label = ['Sunlight', 'Humidity', 'Salt', 'Fertilizer']


    ax.bar(tick_label, height, color = "#c5bea3")
    ax.plot(tick_label, height, color = "#2E8B57")

    plt.scatter(tick_label, height, color = "#000000")

    plt.xticks(rotation = 0, size = 8)
    


    return fig