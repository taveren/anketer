import * as React from "react"

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "destructive" | "outline"
}

function Badge({ className = "", variant = "default", ...props }: BadgeProps) {
  const variantClasses = {
    default: "badge badge-primary",
    secondary: "badge badge-secondary",
    destructive: "badge badge-primary", // Using primary for now
    outline: "badge badge-secondary", // Using secondary for now
  }

  return (
    <div className={`${variantClasses[variant]} ${className}`} {...props} />
  )
}

export { Badge }
