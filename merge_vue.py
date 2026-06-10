import re

with open('components/EntityCreateForm.vue', 'r', encoding='utf-8') as f:
    original = f.read()

with open('components/EntityCreateFormTemplate.vue', 'r', encoding='utf-8') as f:
    new_template = f.read()

# Extract script and style
script_match = re.search(r'(<script.*?<\/script>)', original, re.DOTALL)
style_match = re.search(r'(<style.*?<\/style>)', original, re.DOTALL)

script = script_match.group(1) if script_match else ''
style = style_match.group(1) if style_match else ''

# We need to add defineProps and defineEmits to script
if '<script setup lang="ts">' in script:
    insertion = """
const props = defineProps<{
  activeScreen?: string
}>()
const emit = defineEmits(['update-screen'])

import { watch } from 'vue'

watch(() => props.activeScreen, (newVal) => {
  if (newVal === 'formalizacao') currentStep.value = 1;
  else if (newVal === 'parceria') currentStep.value = 2;
  else if (newVal === 'financeiro') currentStep.value = 3;
}, { immediate: true })

// Override nextStep and prevStep to emit events
"""
    # Let's just modify the script to emit update-screen on next/prev step if needed.
    # Wait, the original nextStep already increments currentStep.
    # We can just let currentStep increment, and watch it to emit update-screen.
    insertion += """
watch(currentStep, (newVal) => {
  if (newVal === 1) emit('update-screen', 'formalizacao');
  else if (newVal === 2) emit('update-screen', 'parceria');
  else if (newVal === 3) emit('update-screen', 'financeiro');
})
"""
    script = script.replace('<script setup lang="ts">', '<script setup lang="ts">\n' + insertion)

# Write merged file
with open('components/EntityCreateForm.vue', 'w', encoding='utf-8') as f:
    f.write(new_template + '\n' + script + '\n' + style)

print("Merged successfully.")
