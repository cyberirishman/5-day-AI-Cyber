Neural Network Training Animations

Interactive, single-file HTML/JavaScript animations that show how a single neuron learns its weight and bias through gradient descent 
— no libraries, no build step, no server. Just open a file in any browser.

The teaching idea: a single neuron computing price = w · bedrooms + b is exactly the same model as linear regression. 
Classical regression solves for the best-fit line in one shot with a formula; a neural network learns the same answer step by step. 
These animations let you watch that happen.

The animations
1. neuron-training-animation-v3.html — fitting a line to data

Five houses (1 bedroom = $200k up to 5 bedrooms = $400k) sit on a straight line.
The neuron starts with a randomly assigned weight and bias — drawn as a badly placed line — and gradient descent nudges both about 20 times until
the line lands exactly on the true pricing rule: $50,000 per bedroom + $150,000 base.

You see the neuron diagram with previous values (orange) and updated values (green) for w and b at every step, the prediction line converging 
onto the dashed least-squares target, and a training-history table of w, b, and the average prediction error in dollars.

2. neuron-two-houses-v3.html — one house at a time (stochastic gradient descent)

The same idea with the abstraction stripped away: only two houses (2 bedrooms / $250k and 4 bedrooms / $350k),
and each training step uses just one of them, alternating A, B, A, B… — stochastic gradient descent with batch size 1, which is how real neural networks train.

Every step plays out in three watchable phases: the forward pass (the bedroom count travels the input wire, 
is multiplied by w, and a predicted price comes out), the error (predicted vs. actual price, gap shown in dollars), 
and the backward pass (Δw and Δb correction chips flow backwards along the wires and the weight and bias update). 
Input, output, error, and correction are all directly visible and traceable.

Controls

Both animations have Play/Pause (run all 20 steps), Step (one training cycle at a time — ideal while presenting), 
Reset (new random starting weight and bias), and an animation speed control.
In the two-houses animation the speed box goes 1–9 (5 = normal, 1 = slow enough to narrate over).

How the math works

Each step computes the prediction error, then follows the gradient of the mean-squared error downhill: w ← w − η·∂L/∂w, b ← b − η·∂L/∂b. 
As is standard machine-learning practice, the input is normalized before training (bedrooms minus the average)
so both parameters converge in ~20 steps; the displayed w and b are always the real-dollar slope and intercept.
The dashed "target" line is the closed-form least-squares solution — the neuron never sees it, it just arrives there.

Running

Download any .html file and double-click it, or serve the folder and open it in a browser. Everything (styles, logic, data) is inside 
the single file. Dark mode follows your system preference.

Older numbered versions (-v1, -v2) are kept intact as history; the highest version number is the current one.
