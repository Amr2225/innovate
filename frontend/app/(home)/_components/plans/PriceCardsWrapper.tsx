import React from "react";
import PriceCards from "./PriceCards";
import { getPlans } from "@/apiService/planService";

export default async function PriceCardsWrapper() {
  const plans = await getPlans();
  console.log(plans[0].description);

  return (
    <div className='flex flex-col md:flex-row gap-2 gap-y-8 items-center justify-between overflow-y-hidden pb-3'>
      {plans.map((plan) => (
        <PriceCards key={plan.id} {...plan} />
      ))}
    </div>
  );
}
