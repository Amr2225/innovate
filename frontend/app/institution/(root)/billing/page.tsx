"use client";
import React, { startTransition, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import CreditsInput from "./_components/creditsInput";
import { buyCredits } from "@/actions/payment";
import { getInstitutionBillingHistory, getInstitutionCurrentPlan } from "@/apiService/planService";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import { toast } from "sonner";
import Loader from "@/components/Loader";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { PlusCircle, CheckCircle2 } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import moment from "moment";

// const getInstitutionBillingHistory = async (): Promise<BillingTransaction[]> => {
//   // Simulate API delay
//   await new Promise((resolve) => setTimeout(resolve, 1000));

//   // Mock billing history data
//   return [
//     {
//       id: "tx_1",
//       amount: 99.99,
//       credits: 1000,
//       description: "Gold Plan Purchase",
//       status: "completed",
//       createdAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(), // 7 days ago
//     },
//     {
//       id: "tx_2",
//       amount: 49.99,
//       credits: 500,
//       description: "Silver Plan Purchase",
//       status: "completed",
//       createdAt: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(), // 14 days ago
//     },
//     {
//       id: "tx_3",
//       amount: 199.99,
//       credits: 2500,
//       description: "Diamond Plan Purchase",
//       status: "pending",
//       createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(), // 1 day ago
//     },
//     {
//       id: "tx_4",
//       amount: 29.99,
//       credits: 300,
//       description: "Additional Credits",
//       status: "completed",
//       createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(), // 3 days ago
//     },
//     {
//       id: "tx_5",
//       amount: 149.99,
//       credits: 1500,
//       description: "Premium Plan Upgrade",
//       status: "failed",
//       createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), // 2 days ago
//     },
//   ];
// };

export default function Page() {
  const { user, updateUser } = useAuth();
  const searchParams = useSearchParams();
  const hmac = searchParams.get("hmac");
  const router = useRouter();
  const [isDialogOpen, setIsDialogOpen] = React.useState(false);

  const { data: lastPlan, isLoading: isLastPlanLoading } = useQuery({
    queryKey: ["institution-last-plan"],
    queryFn: () => getInstitutionCurrentPlan(),
  });

  const { data: billingHistory, isLoading: isBillingHistoryLoading } = useQuery({
    queryKey: ["institution-billing-history"],
    queryFn: () => getInstitutionBillingHistory(),
  });

  useEffect(() => {
    if (hmac && user) {
      startTransition(async () => {
        const isPaymentVerified = await buyCredits(hmac);
        if (isPaymentVerified.isSuccess) {
          toast.success("Payment successful");
          updateUser();
        } else {
          toast.error(isPaymentVerified.message || "Payment failed");
        }
        router.replace("/institution/billing");
      });
    }
  }, [hmac, user, updateUser, router]);

  if (!user) return null;
  if (isLastPlanLoading || !lastPlan || isBillingHistoryLoading) return <Loader />;

  return (
    <div className='container mx-auto py-8'>
      <div className='flex justify-between items-center mb-8'>
        <div className=''>
          <div className='flex items-center gap-2'>
            <h1 className='text-3xl font-bold mb-2'>Billing & Credits</h1>
            <div className='flex items-center gap-4'>
              <Badge variant={lastPlan.type} className='text-base px-4 py-1'>
                {lastPlan.type}
              </Badge>
            </div>
          </div>
        </div>

        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button className='flex items-center gap-2 bg-primary hover:bg-primary/90'>
              <PlusCircle className='w-4 h-4' />
              Add Credits
            </Button>
          </DialogTrigger>
          <DialogContent className='sm:max-w-[500px]'>
            <DialogHeader className='space-y-4'>
              <DialogTitle className='text-2xl font-bold'>Add Credits</DialogTitle>
              <div className='space-y-2'>
                <div className='flex items-center justify-between p-4 bg-muted/50 rounded-lg'>
                  <div>
                    <p className='text-sm text-muted-foreground'>Current Plan</p>
                    <p className='font-semibold'>{lastPlan.type} Plan</p>
                  </div>
                  <Badge variant={lastPlan.type} className='text-sm'>
                    {lastPlan.type}
                  </Badge>
                </div>
              </div>
            </DialogHeader>

            <div className='py-4'>
              <CreditsInput
                name={user.name}
                email={user.email}
                planId={lastPlan.id}
                minimumCredits={lastPlan.minimum_credits}
              />
            </div>

            <div className='p-4 bg-muted/70 rounded-lg'>
              <h4 className='font-medium mb-2'>Plan Benefits</h4>
              <ul className='space-y-2 text-sm text-muted-foreground'>
                {lastPlan.description
                  .filter((plan) => plan.isAdvantage)
                  .map((plan) => (
                    <li key={plan.text} className='flex items-center gap-2'>
                      <CheckCircle2 className='w-4 h-4 text-primary' />
                      <span>{plan.text}</span>
                    </li>
                  ))}
              </ul>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className='bg-white rounded-lg border shadow'>
        <div className='p-6'>
          <h2 className='text-xl font-semibold mb-4'>Billing History</h2>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Order ID</TableHead>
                <TableHead>Transaction ID</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Credits</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {billingHistory?.map((transaction) => (
                <TableRow key={transaction.id}>
                  <TableCell>{transaction.order_id}</TableCell>
                  <TableCell>{transaction.transaction_id}</TableCell>
                  <TableCell>{moment(transaction.valid_from).format("MMM DD, YYYY")}</TableCell>
                  <TableCell>{transaction.credits_amount}</TableCell>
                  <TableCell>{transaction.credits_amount}</TableCell>
                  <TableCell>
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        transaction.payment_status === "True"
                          ? "bg-green-100 text-green-800"
                          : "bg-gray-100 text-gray-800"
                      }`}
                    >
                      {transaction.payment_status === "True" ? "Completed" : "Pending"}
                    </span>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>
    </div>
  );
}
