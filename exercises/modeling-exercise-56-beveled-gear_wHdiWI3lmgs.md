ID: wHdiWI3lmgs
Title: Modeling Exercise 56 - Beveled Gear
Description: This video takes a quick look at basic asset creation in Plasticity.
Duration: 50
Version: 1.2.0
Uploaded: 2023-07-26

Let's build this simple part.

- Start by creating this profile curve using the [[line tool]].

- Use the [[revolve tool]] to create a solid, hide the curve (`H`).

- Select the solid and use the [[delete redundant topology]] command to clean up the solid.

- Create a [[rectangle curve]], extrude it to make a solid. Taper this face, [[rotate]] the new solid 45 degrees.

- Move it so that it intersects with the main solid, then [[radial array]] it to create duplicates.

- Select the main solid followed by the other solids and perform a [[Boolean difference operation]] (`Q`).

- [[Create a hole]] in the center of the solid.

- [[Add fillets]] to all edges and you're good to go.
