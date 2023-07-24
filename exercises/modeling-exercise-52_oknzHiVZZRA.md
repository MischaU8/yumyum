ID: oknzHiVZZRA
Title: Modeling Exercise 52
Description: This video takes a quick look at basic asset creation in Plasticity.
Duration: 60
Version: 1.2.0
Uploaded: 2023-07-17

Let's build this simple part.

- Start by creating two [[circle curves]].

- Use the [[bridge curves tool]] to create a new curve that connects the circles and disable the *trim* attribute.

- Use the [[line curve tool]] to create the bottom part of the main shape, then [[offset]] the two circle curves by pressing the `O` key.

- [[Extrude]] these faces then adjust the results to your liking.

- [[Hide the curves]] then select all solids and perform a [[Boolean Union]] operation (with `Q Q`).

- Create a new [[line curve]] along the bottom.

- Press `Shift-I` for [[imprint curve]] then select the solid as the target.

- Offset this face.

- Create a new [[rectangle curve]] and use it to [[cut]] the solid, then remove the new solid in the rectangle curve.

- Cut two holes into the solid and you're all set.
