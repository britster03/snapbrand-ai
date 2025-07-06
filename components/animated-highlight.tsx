import * as React from "react"
import { cn } from "@/lib/utils"
import { motion } from "framer-motion"

type AnimatedHighlightProps = {
  icon: React.ReactElement
  text: string
  className?: string
}

const AnimatedHighlight: React.FC<AnimatedHighlightProps> = ({ icon, text, className }) => {
  return (
    <motion.div 
      className={cn("flex items-center space-x-3 p-3 rounded-lg bg-white shadow-sm border border-gray-100", className)}
      whileHover={{ scale: 1.02, boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)" }}
      transition={{ duration: 0.3 }}
    >
      <div className="text-blue-600">{icon}</div>
      <span className="text-gray-700 font-medium">{text}</span>
    </motion.div>
  )
}

AnimatedHighlight.displayName = "AnimatedHighlight"

export { AnimatedHighlight } 