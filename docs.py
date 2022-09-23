import streamlit as st


def intro_1():
    st.title("Classic and Quantum Edge Detection Tutorial")
    st.write(
        """
        ### 1) Let's get edge of the image by using various classical method!

        - Sobel
        **[OpenCV Sobel](https://docs.opencv.org/3.4/d2/d2c/tutorial_sobel_derivatives.html)**
        - Prewitt
        - Laplacian
        **[OpenCV Laplace](https://docs.opencv.org/3.4/d5/db5/tutorial_laplace_operator.html)**
        - Canny
        **[OpenCV Canny](https://docs.opencv.org/4.x/da/d22/tutorial_py_canny.html)**
        
        **[Scikit-Image Edge Operator](https://scikit-image.org/docs/stable/auto_examples/edges/plot_edge_filter.html#sphx-glr-auto-examples-edges-plot-edge-filter-py)**
        **[OpenCV Image Gradients](https://docs.opencv.org/4.x/d5/d0f/tutorial_py_gradients.html)**
        
        ### 2) Let's get edge of the image by using QHED method!

        - By using Quantum circuit, we could get edge of the input image.
        - QHED method get edges based on the pixel difference between neighbors
        **[IBM Qiskit QHED tutorial](https://qiskit.org/textbook/ch-applications/quantum-edge-detection.html)**

        ---

        """)
