ID: z6ll7narMRM
Title: Modeling Exercise 53
Description: This video takes a quick look at basic asset creation in Plasticity.
Duration: 50
Version: 1.2.0
Uploaded: 2023-07-19

Let's build this simple part.

- Start by creating a rectangle curve at the origin, create a [[circle curve]] and offset it (`O`).

- Then use the [[bridge curve tool]] to create two new curves that connect the circle and the rectangle curves.

- [[Mirror]] the curves (`alt-X`), then [[extrude]] these faces to create a solid.

- Create a new rectangle curve, followed by a [[180 arc curve]] and a circle curve.

- Then extrude these faces to make a solid.

- Create a new rectangle curve, press `C` for [[cut]] and select the new solid as the target.

- Delete the curve in the new solid, select both solids and perform a [[boolean union operation]] (`Q Q`).

- [[Add fillets]] to all edges and you're good to go.
