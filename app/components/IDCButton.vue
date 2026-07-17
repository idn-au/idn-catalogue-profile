<script setup lang="ts">
import type { HTMLAttributes } from "vue";
import type {ButtonVariants} from "~/components/ui/button";
import type {CustomIDCButtonVariants, IDCButtonVariants} from "~/utils/types";
import { cn } from "~/lib/utils";

const props = defineProps<{
	variant?: IDCButtonVariants;
	size?: ButtonVariants["size"];
	asChild?: boolean;
	disabled?: boolean;
	class?: HTMLAttributes["class"];
}>();

const variantClasses: Record<CustomIDCButtonVariants, HTMLAttributes["class"]> = {
	"red": "bg-isu-red !text-isu-red-foreground hover:bg-isu-red/90 hover:no-underline!",
	"yellow": "bg-isu-yellow !text-isu-yellow-foreground hover:bg-isu-yellow/90 hover:no-underline!",
	"green": "bg-isu-green !text-isu-green-foreground hover:bg-isu-green/90 hover:no-underline!",
	"blue": "bg-isu-blue !text-isu-blue-foreground hover:bg-isu-blue/90 hover:no-underline!",
	"black": "dark bg-background text-foreground hover:bg-background/90 hover:no-underline!",
	"dark-ghost": "",
};
</script>

<template>
	<Button
		:variant="props.variant in Object.keys(variantClasses) ? 'default' : props.variant"
		:size="props.size"
		:class="cn('', props.variant in Object.keys(variantClasses) ? '' : variantClasses[props.variant], props.class)"
		:disabled="props.disabled"
		:asChild="props.asChild"
	>
		<slot />
	</Button>
</template>
