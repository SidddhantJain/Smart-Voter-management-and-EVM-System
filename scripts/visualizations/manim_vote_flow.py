from manim import *


class VoteFlowScene(Scene):
    def construct(self):
        # Entities
        voter = (
            RoundedRectangle(width=3.5, height=1.2, corner_radius=0.2)
            .set_fill("#8fd3f4", opacity=0.7)
            .set_stroke("#2a7fbd", width=2)
        )
        voter_text = Text("Voter Terminal", font_size=28).move_to(voter.get_center())
        voter_group = VGroup(voter, voter_text).to_edge(LEFT).shift(UP * 2)

        encrypt = (
            RoundedRectangle(width=3.5, height=1.2, corner_radius=0.2)
            .set_fill("#4db6ac", opacity=0.7)
            .set_stroke("#00796b", width=2)
        )
        encrypt_text = Text("Encrypt (Fernet)", font_size=28).move_to(
            encrypt.get_center()
        )
        encrypt_group = VGroup(encrypt, encrypt_text).next_to(
            voter_group, RIGHT, buff=2
        )

        tx = (
            RoundedRectangle(width=3.5, height=1.2, corner_radius=0.2)
            .set_fill("#f9a825", opacity=0.7)
            .set_stroke("#bf7f10", width=2)
        )
        tx_text = Text("Vote TX", font_size=28).move_to(tx.get_center())
        tx_group = VGroup(tx, tx_text).next_to(encrypt_group, RIGHT, buff=2)

        mempool = (
            RoundedRectangle(width=3.5, height=1.2, corner_radius=0.2)
            .set_fill("#e0e0e0", opacity=0.9)
            .set_stroke("#616161", width=2)
        )
        mempool_text = Text("Mempool", font_size=28).move_to(mempool.get_center())
        mempool_group = VGroup(mempool, mempool_text).next_to(tx_group, RIGHT, buff=2)

        # Blockchain stack
        block_new = (
            Rectangle(width=3.5, height=1.2)
            .set_fill("#9575cd", opacity=0.9)
            .set_stroke("#4527a0", width=2)
        )
        block_new_text = Text("Block #102", font_size=28).move_to(
            block_new.get_center()
        )
        block_new_group = (
            VGroup(block_new, block_new_text).to_edge(RIGHT).shift(DOWN * 1)
        )

        block_prev = (
            Rectangle(width=3.5, height=1.2)
            .set_fill("#7986cb", opacity=0.9)
            .set_stroke("#283593", width=2)
        )
        block_prev_text = Text("Block #101", font_size=24).move_to(
            block_prev.get_center()
        )
        block_prev_group = VGroup(block_prev, block_prev_text).next_to(
            block_new_group, DOWN, buff=0.2
        )

        block_prev2 = (
            Rectangle(width=3.5, height=1.2)
            .set_fill("#64b5f6", opacity=0.9)
            .set_stroke("#1565c0", width=2)
        )
        block_prev2_text = Text("Block #100", font_size=24).move_to(
            block_prev2.get_center()
        )
        block_prev2_group = VGroup(block_prev2, block_prev2_text).next_to(
            block_prev_group, DOWN, buff=0.2
        )

        chain_label = Text("Blockchain Ledger", font_size=28).next_to(
            block_new_group, UP
        )

        # Arrows
        a1 = Arrow(voter_group.get_right(), encrypt_group.get_left(), buff=0.2)
        a2 = Arrow(encrypt_group.get_right(), tx_group.get_left(), buff=0.2)
        a3 = Arrow(tx_group.get_right(), mempool_group.get_left(), buff=0.2)
        a4 = Arrow(mempool_group.get_bottom(), block_new_group.get_top(), buff=0.2)

        # Build scene
        self.play(FadeIn(voter_group))
        self.play(FadeIn(encrypt_group), GrowArrow(a1))
        self.play(FadeIn(tx_group), GrowArrow(a2))
        self.play(FadeIn(mempool_group), GrowArrow(a3))
        self.play(
            FadeIn(block_new_group),
            FadeIn(block_prev_group),
            FadeIn(block_prev2_group),
            FadeIn(chain_label),
        )
        self.play(GrowArrow(a4))

        # Highlight inclusion
        tx_box = SurroundingRectangle(tx_group, color=YELLOW, buff=0.1)
        blk_box = SurroundingRectangle(block_new_group, color=GREEN, buff=0.1)
        self.play(Create(tx_box))
        self.wait(0.5)
        self.play(Transform(tx_box, blk_box))
        self.wait(1.5)

        # Final caption
        caption = Text(
            "Encrypted vote → included in Block #102 → appended to blockchain",
            font_size=26,
        )
        caption.to_edge(DOWN)
        self.play(Write(caption))
        self.wait(2)
