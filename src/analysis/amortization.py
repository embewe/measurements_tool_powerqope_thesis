import numpy as np
import matplotlib.pyplot as plt

# not used
DOH_H2_SETTINGS_AND_HEADER_PADDED = 93 + 51 + 33 + 240
DOH_POST_PER_QUERY_PADDED = 46

MTU = 1500
IPV4_HEADER = 20
TCP_HEADER = 20
UDP_HEADER = 8 
TLS_HEADER = 5
MAX_TLS_PKT = MTU - IPV4_HEADER - TCP_HEADER - TLS_HEADER

TCP_HANDSHAKE = 2 * (TCP_HEADER + IPV4_HEADER)
TCP_OVERHEAD = TCP_HEADER + IPV4_HEADER
TLS_OVERHEAD = TLS_HEADER + TCP_OVERHEAD
TLS_CLIENT_HELLO = TLS_OVERHEAD + 215
TLS_CLIENT_DONE = TLS_OVERHEAD + 121
TLS_HANDSHAKE = TLS_CLIENT_HELLO + TLS_CLIENT_DONE

QUERY_CHARACTERS = 10

DO53_QUERY_OVERHEAD = 12 + 4 + 2
DO53_QUERY_SIZE = DO53_QUERY_OVERHEAD + QUERY_CHARACTERS

DOT_STATIC_OVERHEAD = TCP_HANDSHAKE + TLS_HANDSHAKE
DOT_QUERY_OVERHEAD = DO53_QUERY_OVERHEAD + TLS_HEADER
DOT_QUERY_SIZE = DOT_QUERY_OVERHEAD + QUERY_CHARACTERS
MAX_DOT_REQUESTS = np.floor(MAX_TLS_PKT / (DOT_QUERY_OVERHEAD + QUERY_CHARACTERS))

DOH_H2_SETTINGS_AND_HEADER = TLS_OVERHEAD + 69 + 27 + 9 + 216
DOH_STATIC_OVERHEAD = TCP_HANDSHAKE + TLS_HANDSHAKE + DOH_H2_SETTINGS_AND_HEADER
DOH_QUERY_H2_HEADER = 13
DOH_QUERY_H2_FRAME = 9
DOH_QUERY_OVERHEAD = DOT_QUERY_OVERHEAD + DOH_QUERY_H2_HEADER + DOH_QUERY_H2_FRAME
DOH_QUERY_SIZE = DOH_QUERY_OVERHEAD + QUERY_CHARACTERS
MAX_DOH_REQUESTS = np.floor(MAX_TLS_PKT / (DOH_QUERY_OVERHEAD + QUERY_CHARACTERS))


def amortization(xlimit, filename):
    requests = np.arange(1, 105)

    # Compute bytes sent for each request for DoT
    bytes_dot = [TCP_OVERHEAD * np.ceil(r / MAX_DOT_REQUESTS) +
                 (r * DOT_QUERY_SIZE) + DOT_STATIC_OVERHEAD for r in requests]
    dot = (requests, bytes_dot)

    print("TCP OVERHEAD", TCP_OVERHEAD)
    print("TLS_HANDSHAKE", TLS_HANDSHAKE)
    print("MAX_DOT_REQUESTS", MAX_DOT_REQUESTS)
    print("DOT_QUERY_SIZE", DOT_QUERY_SIZE)
    print("DOT_STATIC_OVERHEAD", DOT_STATIC_OVERHEAD)
    

    # Compute bytes sent for "r" requests for DoH
    bytes_doh = [TCP_OVERHEAD * np.ceil(r / MAX_DOH_REQUESTS) +
                 (r * DOH_QUERY_SIZE) + DOH_STATIC_OVERHEAD for r in requests]
    doh = (requests, bytes_doh)

    # Compute bytes setn for "r" requests for Do53
    bytes_do53 = [(UDP_HEADER + IPV4_HEADER + DO53_QUERY_SIZE) * r for r in requests]
    do53 = (requests, bytes_do53)

    print(bytes_do53[22])
    print(bytes_dot[22])

    all_data = {"Do53": {"data": do53, "color": "black", "linestyle": "-"},
                "DoT":  {"data": dot,  "color": "#0072B2", "linestyle": "-"},
                "DoH":  {"data": doh,  "color": "#A60628",  "linestyle": "-"}}
    plot_amortization(all_data, xlimit, filename)


def plot_amortization(all_data, xlimit, filename):
    # Set up the plot
    plt.figure()
    margin = .033333333

    # Plot the CDF
    fig, ax = plt.subplots()
    ax.set_xlim([- margin * xlimit, xlimit * (1 + margin)])
    ax.set_xticks([1, 20, 40, 60, 80, 100])
    # ax.set_ylim([-0.05, 1.05])

    for key in sorted(all_data.keys()):
        data = all_data[key]
        d = data["data"]
        color = data["color"]
        linestyle = data["linestyle"]

        x = d[0]
        y = d[1]
        ax.step(x, y, linewidth=1.5, color=color, linestyle=linestyle,
                label=key)

    # Set up the labels/legend
    plt.xlabel('DNS Requests')
    plt.ylabel('Bytes Sent')
    legend = plt.legend(loc='lower right')
    legend.get_frame().set_linewidth(1)
    plt.savefig(filename, bbox_inches='tight')


if __name__ == "__main__":
    amortization(100, "amortization.pdf")
