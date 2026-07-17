import type {ButtonVariants} from "~/components/ui/button";

export type CustomIDCButtonVariants = "red" | "yellow" | "green" | "blue" | "black" | "dark-ghost";

export type IDCButtonVariants = ButtonVariants["variant"] | CustomIDCButtonVariants;
