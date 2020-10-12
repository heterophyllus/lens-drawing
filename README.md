# Python Program for Lens Drawing


## Summary
This python program plots an aspherical curve and draws a lens shape.


## Usage

### 1. Using the module
Each of the modules can be used in any codes like the following example.

```python
# single surface plot

import surface as sf
import numpy as np
import matplotlib.pyplot as plt

s = sf.EvenAsphere(r=29.324,
                    k=0.3518,
                coefs=[-0.1071e-5,
                        -0.1440e-8,
                        -0.3022e-12,
                        -0.5736e-14,
                        0.59e-17,
                        -0.1142e-19])

h = np.arange(0,25,0.25)
s.print_data(h)

plt.plot(h,s.sag(h))
```

### 2. GUI application
The GUI application is available by running the below in the directory. The executable is also distributed on the [Release page](https://github.com/heterophyllus/lens-drawing/releases/latest).
```
python drawing-gui.py
```

<img src= "https://github.com/heterophyllus/lens-drawing/blob/master/images/demo.png" width="50%">

## License
This project is licensed under GPL license.  See [LICENSE](LICENSE.md) for details.


## Contributing
Contributions and feedbacks are greatly appreciated.
Please read [CONTRIBUTING](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

